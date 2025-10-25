from models.transaction import Transaction
from models.payment import Payment
from models.fee import Fee
from models.contract import Contract
from app import db
from decimal import Decimal 
import requests
import time
import hmac
import hashlib
import json
import uuid


class TransactionService:
    @staticmethod
    def get_transaction_by_seller_id(seller_id):
        return Transaction.query.filter_by(seller_id=seller_id).all()
    
    @staticmethod
    def get_transaction_by_buyer_id(buyer_id):
        return Transaction.query.filter_by(buyer_id=buyer_id).all()
    

    @staticmethod
    def get_transaction_by_id(transaction_id): 
        return Transaction.query.get(transaction_id)

    @staticmethod
    def get_contract_by_transaction_id(transaction_id): 
        return Contract.query.filter_by(transaction_id=transaction_id).first()

    @staticmethod
    def create_transaction(listing_id, seller_id, buyer_id, final_price, transaction_status='pending'): 
        try:
            seller_id = int(seller_id)
            buyer_id = int(buyer_id)
            listing_id = int(listing_id)
            final_price = float(final_price)
        except (TypeError, ValueError):
            return None, None, "Invalid input data type."

        if seller_id == buyer_id:
            return None, None, "you sell this list."
        listing = Transaction.query.filter_by(listing_id=listing_id).first()
        if listing:
            return None, None, "someone has bought this list."
        try:
            new_transaction = Transaction(
                listing_id=listing_id,
                seller_id=seller_id,
                buyer_id=buyer_id,
                final_price=final_price,
                transaction_status=transaction_status
            )
            db.session.add(new_transaction) 
            db.session.flush() 
             
            new_contract = Contract(
                transaction_id=new_transaction.transaction_id,
                term = f"""Hợp đồng giao dịch #{new_transaction.transaction_id}:
                        Bên {new_transaction.seller_id} cung cấp hàng hóa/dịch vụ cho Bên {new_transaction.buyer_id} theo thỏa thuận.
                        Giá trị hợp đồng: {new_transaction.final_price} VNĐ.
                        Bên {new_transaction.seller_id} đảm bảo chất lượng và giao đúng hạn; Bên {new_transaction.buyer_id} thanh toán đầy đủ, đúng thời hạn.
                        Hai bên cam kết thực hiện đúng nghĩa vụ, không đơn phương hủy bỏ khi chưa thống nhất.
                        Mọi tranh chấp sẽ được giải quyết bằng thương lượng, nếu không thì theo pháp luật hiện hành.
                        Hợp đồng có hiệu lực kể từ khi giao dịch được xác nhận thành công.""",
                signed_by_seller=False,
                signed_by_buyer=False
            )
            db.session.add(new_contract)
            
            db.session.commit()
            return new_transaction, new_contract, "Transaction và Contract đã được tạo thành công."
        except Exception as e:
            db.session.rollback()
            return None, None, f"Lỗi khi tạo transaction: {str(e)}"

    @staticmethod
    def sign_contract(transaction_id, user_id): 
        transaction = TransactionService.get_transaction_by_id(transaction_id)
        if not transaction:
            return None, "Transaction không tìm thấy."

        contract = TransactionService.get_contract_by_transaction_id(transaction_id)
        if not contract:
            return None, "Contract không tìm thấy."

        if transaction.transaction_status != 'pending':
            return None, f"Không thể ký. Trạng thái giao dịch là: {transaction.transaction_status}"

        # Xác định vai trò của user
        if user_id == transaction.buyer_id:
            if contract.signed_by_buyer:
                return contract, "Bạn đã ký hợp đồng này rồi."
            contract.signed_by_buyer = True
            message = "Người mua đã ký hợp đồng."
        elif user_id == transaction.seller_id:
            if contract.signed_by_seller:
                return contract, "Bạn đã ký hợp đồng này rồi."
            contract.signed_by_seller = True
            message = "Người bán đã ký hợp đồng."
        else:
            return None, "Bạn không có quyền ký hợp đồng này."

        # Logic 3 (tiếp): Kiểm tra nếu cả hai đã ký
        if contract.signed_by_buyer and contract.signed_by_seller:
            transaction.transaction_status = 'awaiting_payment'
            message += " Cả hai bên đã ký. Giao dịch chuyển sang trạng thái chờ thanh toán."

        db.session.commit()
        return contract, message

    @staticmethod
    def create_payment(transaction_id, payment_method, amount, payment_status='initiated'):
        transaction = TransactionService.get_transaction_by_id(transaction_id)
        if not transaction:
            return None, "Transaction không tồn tại"
            
        if transaction.transaction_status != 'awaiting_payment':
            return None, "Giao dịch chưa sẵn sàng để thanh toán. Hợp đồng cần được ký bởi cả hai bên."

        existing_payment = Payment.query.filter_by(
            transaction_id=transaction_id, 
            payment_status='initiated'
        ).first()
        if existing_payment: 
            return None, "Bạn đã yêu cầu thanh toán sản phẩm này."

        new_payment = Payment(
            transaction_id=transaction_id,
            payment_method=payment_method,
            amount=amount,
            payment_status=payment_status
        )
        db.session.add(new_payment)
        db.session.commit()
        return new_payment, "Thanh toán đã được khởi tạo thành công."


    @staticmethod
    def update_transaction_status(transaction_id, new_status):
        transaction = TransactionService.get_transaction_by_id(transaction_id)
        if not transaction:
            return None, "Transaction không tìm thấy."

        payment = Payment.query.filter_by(transaction_id=transaction_id, payment_status='initiated').first()

        if new_status == 'paid':
            if transaction.transaction_status == 'paid':
                return transaction, "Transaction đã được thanh toán trước đó."
            
            transaction.transaction_status = 'paid'
            if payment:
                payment.payment_status = 'completed'
            
            try:
                fee_rate = Decimal('0.025') 
                fee_amount = transaction.final_price * fee_rate
                
                new_fee = Fee(
                    transaction_id=transaction_id,
                    amount=fee_amount,
                    fee_status='collected'
                )
                db.session.add(new_fee)
                message = "Transaction đã được thanh toán và Phí đã được ghi nhận."
            except Exception as e:
                message = f"Transaction đã thanh toán, nhưng lỗi khi tạo Phí: {str(e)}"

        elif new_status == 'failed':
            if payment:
                payment.payment_status = 'failed' 
            message = "Thanh toán thất bại."
        
        elif new_status == 'pending': 
            contract = TransactionService.get_contract_by_transaction_id(transaction_id)
            if contract and (contract.signed_by_buyer or contract.signed_by_seller):
                return None, "Không thể reset về 'pending' vì hợp đồng đã được ký."
            transaction.transaction_status = 'pending'
            message = "Transaction đã được reset về 'pending'."

        else: 
            transaction.transaction_status = new_status
            message = f"Transaction status đã được cập nhật thành {new_status}."

        db.session.commit()
        return transaction, message

    @staticmethod
    def cancel_transaction(transaction_id):
        """Hủy giao dịch (DELETE)."""
        transaction = Transaction.query.get(transaction_id)
        if transaction: 
            if transaction.transaction_status in ['paid']:
                 return False, "Không thể hủy giao dịch đã thanh toán."
            Payment.query.filter_by(transaction_id=transaction_id).delete()
            Contract.query.filter_by(transaction_id=transaction_id).delete()
            Fee.query.filter_by(transaction_id=transaction_id).delete()

            db.session.delete(transaction)
            db.session.commit()
            return True, "Giao dịch đã được hủy."
        return False, "Transaction không tìm thấy."



    @staticmethod
    def call_momo_api(order_id, amount, order_info, return_url, notify_url):
        endpoint = "https://test-payment.momo.vn/v2/gateway/api/create"
        partnerCode = "MOMO"
        accessKey = "F8BBA842ECF85"
        secretKey = "K951B6PE1waDMi640xX08PD3vg6EkVlz"

        requestId = str(uuid.uuid4())
        orderId = f"{order_id}-{int(time.time())}"
        extraData = ""
        requestType = "captureWallet"   
        amount_int = int(amount)
        ipnUrl = notify_url
 
        raw_signature = (
            f"accessKey={accessKey}"
            f"&amount={amount_int}"
            f"&extraData={extraData}"
            f"&ipnUrl={ipnUrl}"
            f"&orderId={orderId}"
            f"&orderInfo={order_info}"
            f"&partnerCode={partnerCode}"
            f"&redirectUrl={return_url}"
            f"&requestId={requestId}"
            f"&requestType={requestType}"
        )

        signature = hmac.new(
            secretKey.encode('utf-8'),
            raw_signature.encode('utf-8'),
            hashlib.sha256
        ).hexdigest() 
        data = {
            "partnerCode": partnerCode,
            "orderId": orderId,
            "requestId": requestId,
            "amount": str(int(amount)),
            "orderInfo": order_info,
            "redirectUrl": return_url,
            "ipnUrl": ipnUrl,
            "extraData": extraData,
            "requestType": requestType,
            "signature": signature
        }

        headers = {'Content-Type': 'application/json'} 
        response = requests.post(endpoint, json=data, headers=headers)
        try:
            result = response.json()
        except Exception as e:
            print("ERROR parsing JSON:", e)
            print("Raw response text:", response.text)
            raise 
        print("\n--- MoMo API DEBUG ---")
        print("Payload:", json.dumps(data, ensure_ascii=False, indent=2))
        print("Raw signature:", raw_signature)
        print("Signature:", signature)
        print("Response:", json.dumps(result, ensure_ascii=False, indent=2))
        print("----------------------\n")

        if response.status_code == 200 and result.get("resultCode") == 0:
            return result["payUrl"]
        else:
            raise Exception(f"🛑 Lỗi MoMo: {json.dumps(result, ensure_ascii=False)}, code: {response.status_code}, Raw signature: {raw_signature}, Signature: {signature}")
    @staticmethod
    def call_vietinbank_api(order_id, amount, order_info, return_url, notify_url): 
        resultCode = 0
        message = "Thanh toan Ngan hang Thanh cong (Mock)"  
        orderId = f"{order_id}-{int(time.time())}"  
        amount_int = int(amount)
        fake_success_url = f"{return_url}?resultCode={resultCode}&message={message}&orderId={orderId}&amount={amount_int}"
        return fake_success_url