from flask import Blueprint, jsonify, request, current_app, redirect
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from functools import wraps
from app import db
from models.transaction import Transaction
from models.contract import Contract
from models.payment import Payment
from models.fee import Fee
import uuid
import os
import requests
import logging
from services.transaction_service import TransactionService
from functools import wraps
from sqlalchemy.orm import joinedload
from decimal import Decimal 

USER_SERVICE_URL = os.environ.get('USER_SERVICE_URL', 'http://user-service:5000')  
LISTING_SERVICE_URL = os.environ.get('LISTING_SERVICE_URL', 'http://listing-service:5001')
REQUEST_TIMEOUT = 1

transaction_api = Blueprint('transaction_api', __name__, url_prefix='/api')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- DECORATOR KIỂM TRA QUYỀN ADMIN ---
def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            verify_jwt_in_request() 
            claims = get_jwt() 
            if claims.get("role") == "admin": 
                return fn(*args, **kwargs)
            else:
                return jsonify({"error": "Admin access required"}), 403
        return decorator
    return wrapper

def internal_or_user_required(): 
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs): 
            logger.debug(f"TRANSACTION_SVC [AUTH]: Đã nhận Headers: {request.headers}")
            try:
                verify_jwt_in_request() 
                return fn(*args, **kwargs)
            except Exception as jwt_exc: 
                internal_token_header = request.headers.get('Authorization')
                api_key_header = request.headers.get('X-Api-Key')
                logger.debug(f"TRANSACTION_SVC [AUTH]: Internal Token Header: {internal_token_header}")
                logger.debug(f"TRANSACTION_SVC [AUTH]: API Key Header: {api_key_header}") 
                correct_internal_token = os.environ.get('INTERNAL_SERVICE_TOKEN')  
                correct_api_key = os.environ.get('INTERNAL_API_KEY')  

                is_valid_internal_call = False 
                if correct_internal_token and internal_token_header == correct_internal_token:
                    is_valid_internal_call = True 
                elif correct_api_key and api_key_header == correct_api_key:
                    is_valid_internal_call = True

                if is_valid_internal_call: 
                    logger.warning("[AUTH] KIỂM TRA AUTH NỘI BỘ THẤT BẠI.")
                    return fn(*args, **kwargs)
                else: 
                    logger.warning(f"Internal/User Auth Failed. JWT Error: {jwt_exc}. Headers: {request.headers}")
                    return jsonify({"error": "Unauthorized access"}), 401
        return decorator
    return wrapper

def get_user_info_by_id(user_id: int):
    """Lấy thông tin user (đặc biệt là username) từ User Service."""
    if not user_id:
        return None
    # Đảm bảo endpoint này tồn tại bên user-service và trả về list chứa user object
    url = f"{USER_SERVICE_URL}/api/info/{user_id}"
    try:
        response = requests.get(url, timeout=REQUEST_TIMEOUT)
        if response.status_code == 200:
            user_data_list = response.json()
            # Kiểm tra xem user-service trả về list đúng không
            if user_data_list and isinstance(user_data_list, list) and len(user_data_list) > 0:
                return user_data_list[0] # Lấy phần tử đầu tiên trong list
            else:
                logger.warning(f"User Service returned empty or invalid list data for user ID {user_id} at {url}")
                return None
        elif response.status_code == 404:
            logger.warning(f"User not found in User Service for ID {user_id} at {url}")
            return None
        else:
            logger.warning(f"User Service returned status {response.status_code} for user ID {user_id} at {url}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to connect to User Service at {url} for user info: {e}")
        return None 

def serialize_payment_for_admin(payment):
    """Chuyển đổi Payment object sang dict cho trang admin, bao gồm username."""
    if not payment: return None

    buyer_username = "N/A"
    seller_username = "N/A"
 
    if payment.transaction and payment.transaction.buyer_id:
        buyer_info = get_user_info_by_id(payment.transaction.buyer_id)
        if buyer_info and 'username' in buyer_info:
            buyer_username = buyer_info['username']
        else: 
            buyer_username = f"ID: {payment.transaction.buyer_id}"
 
    if payment.transaction and payment.transaction.seller_id:
        seller_info = get_user_info_by_id(payment.transaction.seller_id)
        if seller_info and 'username' in seller_info:
            seller_username = seller_info['username']
        else: 
            seller_username = f"ID: {payment.transaction.seller_id}"

    return {
        'payment_id': payment.payment_id,
        'transaction_id': payment.transaction_id,
        'buyer_username': buyer_username,   
        'seller_username': seller_username,  
        'payment_method': payment.payment_method,
        'amount': str(payment.amount),
        'payment_status': payment.payment_status,
        'created_at': payment.created_at.isoformat() if payment.created_at else None
    }

def serialize_transaction(transaction):
    """Chuyển đổi Transaction object sang dict."""
    if not transaction: return None
    return {
        'transaction_id': transaction.transaction_id,
        'listing_id': transaction.listing_id,
        'seller_id': transaction.seller_id,
        'buyer_id': transaction.buyer_id,
        'final_price': str(transaction.final_price), # Dùng string cho an toàn
        'transaction_status': transaction.transaction_status,
        'created_at': transaction.created_at.isoformat() if transaction.created_at else None
    }

def serialize_contract(contract):
    """Chuyển đổi Contract object sang dict."""
    if not contract: return None
    return {
        'contract_id': contract.contract_id,
        'transaction_id': contract.transaction_id,
        'term': contract.term,
        'signed_by_seller': contract.signed_by_seller,
        'signed_by_buyer': contract.signed_by_buyer,
        'created_at': contract.created_at.isoformat() if contract.created_at else None
    }

def serialize_payment(payment):
    """Chuyển đổi Payment object sang dict, bao gồm buyer/seller ID."""
    if not payment: return None
 
    buyer_id = None
    seller_id = None 
    if payment.transaction:
        buyer_id = payment.transaction.buyer_id
        seller_id = payment.transaction.seller_id

    return {
        'payment_id': payment.payment_id,
        'transaction_id': payment.transaction_id,
        'payment_method': payment.payment_method,
        'amount': str(payment.amount),
        'payment_status': payment.payment_status,
        'created_at': payment.created_at.isoformat() if payment.created_at else None,
        'buyer_id': buyer_id,     
        'seller_id': seller_id   
    }

# --- ENDPOINTS ---
@transaction_api.route("/transactions-seller", methods = ['GET'])
@jwt_required()
def get_transaction_by_seller():
    current_user_id = int(get_jwt_identity())
    transactions = TransactionService.get_transaction_by_seller_id(current_user_id)
    if not transactions: return jsonify({"error": "Transaction empty"})
    return jsonify([serialize_transaction(t) for t in transactions]), 200

@transaction_api.route("/transactions-buyer", methods = ['GET'])
@jwt_required()
def get_transaction_by_buyer():
    current_user_id = int(get_jwt_identity())
    transactions = TransactionService.get_transaction_by_buyer_id(current_user_id)
    if not transactions: return jsonify({"error": "Transaction empty"})
    return jsonify([serialize_transaction(t) for t in transactions]), 200

@transaction_api.route("/transactions", methods=['POST'])
@internal_or_user_required()
def create_transaction():
    data = request.get_json()
    if not data: return jsonify({"error": "Missing JSON body"}), 400  
    has_seller = 'seller_id' in data
    has_price = 'final_price' in data
    has_listing = data.get('listing_id') is not None  
    has_auction = data.get('auction_id') is not None  
 
    if not (has_seller and has_price):
         return jsonify({"error": "Thiếu seller_id hoặc final_price"}), 400
 
    if not (has_listing or has_auction):
         return jsonify({"error": "Phải cung cấp listing_id hoặc auction_id"}), 400

    if has_listing and has_auction:
         return jsonify({"error": "Không thể tạo transaction từ cả listing và auction cùng lúc"}), 400

    try:
        current_user_id = int(get_jwt_identity())
    except Exception: 
         current_user_id = data.get('buyer_id')  
         if not current_user_id:
              return jsonify({"error": "Không xác định được người mua (thiếu token hoặc buyer_id)"}), 401

    try: 
        new_transaction, new_contract, message = TransactionService.create_transaction(
            listing_id=data.get('listing_id'),  
            auction_id=data.get('auction_id'),  
            seller_id=data['seller_id'],
            buyer_id=current_user_id,  
            final_price=data['final_price']
        ) 

        if not new_transaction:
             return jsonify({"error": message}), 400 

        return jsonify({
            "message": message,
            "transaction": serialize_transaction(new_transaction),
            "contract": serialize_contract(new_contract)
        }), 201

    except Exception as e:
        logger.error(f"Lỗi khi gọi TransactionService.create_transaction: {e}", exc_info=True)
        return jsonify({"error": f"Lỗi máy chủ nội bộ: {str(e)}"}), 500

@transaction_api.route('/transactions/<int:transaction_id>/contract/sign', methods=['POST'])
@jwt_required()
def sign_contract_route(transaction_id):
    current_user_id = int(get_jwt_identity())
    contract, message = TransactionService.sign_contract(transaction_id, current_user_id)
    
    if not contract:
        status_code = 404 if "không tìm thấy" in message else 403
        return jsonify({"error": message}), status_code
        
    return jsonify({
        "message": message,
        "contract": serialize_contract(contract)
    }), 200

@transaction_api.route('/transactions/<int:transaction_id>/payment/status', methods=['GET'])
@jwt_required()
def get_single_payment_status(transaction_id):  
    try: 
        payment = (
            db.session.query(Payment)
            .options(joinedload(Payment.transaction))  
            .filter(Payment.transaction_id == transaction_id)
            .first()
        )

        if not payment:
            return jsonify({"error": "Sản phẩm này chưa thanh toán hoặc giao dịch không tồn tại."}), 404
        current_user_id = int(get_jwt_identity())
        if payment.transaction.buyer_id != current_user_id and payment.transaction.seller_id != current_user_id:
            return jsonify({"error": "Bạn không có quyền xem trạng thái thanh toán này."}), 403
 
        return jsonify({"payment": serialize_payment(payment)}), 200

    except Exception as e:
        print(f"!!! Lỗi khi lấy payment status cho user {transaction_id}: {e}")
        return jsonify({"error": "Lỗi máy chủ nội bộ"}), 500
#sửa hàm=============
#====================
@transaction_api.route('/transactions/<int:transaction_id>/payment', methods=['POST'])
@jwt_required() 
def create_payment_route(transaction_id): 
    data = request.get_json()
    if not data or not all(k in data for k in ('payment_method', 'amount')):
        return jsonify({"error": "Missing payment_method or amount"}), 400

    current_user_id = int(get_jwt_identity())
    transaction = TransactionService.get_transaction_by_id(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction không tìm thấy"}), 404
    if transaction.buyer_id != current_user_id:
        return jsonify({"error": "Chỉ người mua mới có thể thanh toán."}), 403

    try:
        new_payment, message = TransactionService.create_payment(
            transaction_id=transaction_id,
            payment_method=data['payment_method'],
            amount=data['amount']
        )
        
        if not new_payment: 
            if "Transaction không tồn tại" in message:
                return jsonify({"error": message}), 404
            else:  
                return jsonify({"error": message}), 400 

        return jsonify({
            "message": message,
            "payment": serialize_payment(new_payment)
        }), 201 # 201 Created
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@transaction_api.route('/transactions/<int:transaction_id>/status', methods=['PATCH'])
@jwt_required() 
def update_transaction_status_route(transaction_id): 
    data = request.get_json()
    if not data or 'new_status' not in data:
        return jsonify({"error": "Missing 'new_status' field"}), 400
        
    new_status = data['new_status']
    if new_status not in ['paid', 'failed', 'cancelled', 'pending']:
         return jsonify({"error": "Trạng thái không hợp lệ."}), 400

    updated_transaction, message = TransactionService.update_transaction_status(
        transaction_id=transaction_id,
        new_status=new_status
    )
    
    if not updated_transaction:
        return jsonify({"error": message}), 404
        
    return jsonify({
        "message": message,
        "transaction": serialize_transaction(updated_transaction)
    }), 200

@transaction_api.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@jwt_required()
def cancel_transaction_route(transaction_id): 
    success, message = TransactionService.cancel_transaction(transaction_id)
    if not success:
        return jsonify({"error": message}), 404
        
    return jsonify({"message": message}), 200
 
# --- Sửa endpoint này ---

@transaction_api.route("/my-transactions", methods=['GET'])
@jwt_required()
def get_my_transactions():
    current_user_id = int(get_jwt_identity())
    try: 
        all_payments = (
            db.session.query(Payment)
            .join(Transaction, Payment.transaction_id == Transaction.transaction_id)
            .options(joinedload(Payment.transaction)) 
            .filter(
                Transaction.buyer_id == current_user_id 
            )
            .order_by(Payment.created_at.desc())
            .all()
        )
        if not all_payments:
            return jsonify([]), 200

        return jsonify([serialize_payment(p) for p in all_payments]), 200
    except Exception as e:
         print(f"!!! Lỗi khi lấy my-transactions: {e}")
         return jsonify({"error": "Lỗi máy chủ nội bộ"}), 500
    
@transaction_api.route("/transactions/<int:transaction_id>/contract", methods=["GET"])
@jwt_required()
def get_contract(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    contract = Contract.query.filter_by(transaction_id=transaction_id).first()

    if not contract:
        return jsonify({"error": "Không tìm thấy hợp đồng."}), 404

    return jsonify({
        "transaction": serialize_transaction(transaction),
        "contract": serialize_contract(contract)
    }), 200


@transaction_api.route('/transactions/<int:transaction_id>/confirm-payment', methods=['POST'])
@jwt_required()
def confirm_payment_route(transaction_id):  
    data = request.get_json()
    if not data or 'payment_method' not in data:
        return jsonify({"error": "Missing payment_method"}), 400

    current_user_id = int(get_jwt_identity())
    transaction = TransactionService.get_transaction_by_id(transaction_id)
    if not transaction:
        return jsonify({"error": "Transaction không tìm thấy"}), 404
    if transaction.buyer_id != current_user_id:
        return jsonify({"error": "Chỉ người mua mới có thể thanh toán."}), 403

    payment = Payment.query.filter_by(
        transaction_id=transaction_id,
        payment_status='initiated'
    ).first()

    if not payment:
        return jsonify({"error": "Không có thanh toán nào đang chờ xử lý."}), 400

    payment_method = payment.payment_method
    amount = payment.amount

    try:
        order_info = f"Thanh toán giao dịch #{transaction_id}"
        return_url = "http://localhost:8080/payment-result"
        notify_url = "https://dancetta-aggadic-marla.ngrok-free.dev/transaction/api/payments/webhook/momo"

        if payment_method == 'e-wallet':
            payment_url = TransactionService.call_momo_api(
                order_id=transaction_id,
                amount=amount,
                order_info=order_info,
                return_url=return_url,
                notify_url=notify_url
            )
        elif payment_method == 'bank':
            payment_url = TransactionService.call_vietinbank_api(
                order_id=transaction_id,
                amount=amount,
                order_info=order_info,
                return_url=return_url,
                notify_url=notify_url 
            )
            try: 
                payment.payment_status = 'pending'
                transaction.transaction_status = 'paid'
                auction_id = transaction.auction_id
                listing_id = transaction.listing_id 
                if listing_id:
                    internal_token = current_app.config.get('INTERNAL_SERVICE_TOKEN')
                    if not internal_token:
                        logger.error("INTERNAL_SERVICE_TOKEN bị thiếu hoặc sai định dạng.")
                        db.session.rollback()
                        raise Exception("Lỗi cấu hình máy chủ nội bộ.")
                    headers = {'Authorization': internal_token}
                    url = f"{LISTING_SERVICE_URL}/api/listings/{listing_id}/status"
                    payload = {'status': 'sold'} 
                    response = requests.put(
                        url, 
                        json=payload, 
                        headers=headers, 
                        timeout=REQUEST_TIMEOUT
                    )
                    response.raise_for_status() 
                db.session.commit()
                logger.info(f"Bank Payment: Xử lý thành công TXN {transaction_id}. Payment -> 'pending'.")
            
            except requests.exceptions.RequestException as e: 
                db.session.rollback()  
                logger.error(f"confirm_payment (bank): Lỗi khi gọi Listing Service (Listing {listing_id}). Đã rollback. Lỗi: {e}")
                raise Exception(f"Lỗi khi cập nhật trạng thái sản phẩm: {e}")
            
            except Exception as e: 
                db.session.rollback()  
                logger.error(f"confirm_payment (bank): Lỗi CSDL hoặc cấu hình khi commit TXN {transaction_id}. Lỗi: {e}")
                raise e  
        else:
            return jsonify({"error": "Phương thức thanh toán không hợp lệ."}), 400 
        return jsonify({
            "message": f"Tạo thanh toán {payment_method.upper()} thành công",
            "payment_url": payment_url
        }), 200

    except Exception as e: 
        logger.error(f"Lỗi nghiêm trọng khi confirm_payment cho TXN {transaction_id}: {e}")
        return jsonify({"error": str(e)}), 500

@transaction_api.route('/payments/webhook/momo', methods=['POST'])
def momo_webhook(): 
    data = request.get_json()
    order_id = data.get('orderId')
    result_code = data.get('resultCode') 
    if order_id is None or result_code is None: 
        return jsonify({"error": "Missing data"}), 400  
    try:
        transaction_id_str = order_id.split('-')[0]
        if not transaction_id_str.isdigit():
             return jsonify({"error": "Invalid orderId format"}), 400
        transaction_id = int(transaction_id_str)
    except Exception as e:
        return jsonify({"error": "Invalid orderId"}), 400  
    try:
        payment = Payment.query.filter_by(transaction_id=transaction_id).first()
    except Exception as e: 
        return jsonify({"error": "Database query error"}), 500

    if not payment:
        return jsonify({"error": "Payment not found"}), 404  
    if payment.payment_status in ['pending', 'completed']:
        return jsonify({"status": "ok"}), 200 
    if payment.payment_status == 'initiated': 
        if result_code == 0: 
            try: 
                payment.payment_status = 'pending' 
                transaction = Transaction.query.get(payment.transaction_id)
                if not transaction:
                    db.session.rollback()
                    return jsonify({"error": "Dữ liệu nội bộ không nhất quán"}), 500 
                transaction.transaction_status = 'paid'
                auction_id = transaction.auction_id
                listing_id = transaction.listing_id 
                if listing_id:
                    internal_token = current_app.config.get('INTERNAL_SERVICE_TOKEN')
                    if not internal_token:
                        db.session.rollback()
                        return jsonify({"error": "Lỗi cấu hình máy chủ nội bộ."}), 500
                    headers = {'Authorization': internal_token}
                    url = f"{LISTING_SERVICE_URL}/api/listings/{listing_id}/status"
                    payload = {'status': 'sold'} 
                    response = requests.put(
                        url, 
                        json=payload, 
                        headers=headers, 
                        timeout=REQUEST_TIMEOUT
                    )
                    response.raise_for_status() 
                db.session.commit()
            except requests.exceptions.RequestException as e:
                db.session.rollback()
                return jsonify({"error": "Failed to update listing service"}), 500
            except Exception as e: 
                db.session.rollback()
                return jsonify({"error": "Database commit error"}), 500
        else:
            payment.payment_status = 'failed'
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": "Database commit error"}), 500
    return jsonify({"status": "ok"}), 200

@transaction_api.route('/transactions/<int:transaction_id>/payment-status', methods=['GET'])
@jwt_required()
def get_the_payment_status_for_polling(transaction_id):  
    try:
        current_user_id = int(get_jwt_identity()) 
        payment = db.session.query(Payment.payment_status)\
            .join(Transaction)\
            .filter(Payment.transaction_id == transaction_id, Transaction.buyer_id == current_user_id)\
            .scalar()  

        if payment is None: 
             transaction_exists = db.session.query(Transaction.transaction_id)\
                 .filter(Transaction.transaction_id == transaction_id, Transaction.buyer_id == current_user_id)\
                 .count() > 0
             if not transaction_exists:
                 return jsonify({"error": "Không tìm thấy giao dịch hoặc không có quyền truy cập."}), 404
             else: 
                 return jsonify({"status": "initiated"}), 200  

        return jsonify({"status": payment}), 200

    except Exception as e:
        print(f"!!! Lỗi khi kiểm tra status polling: {e}")
        return jsonify({"error": "Lỗi máy chủ nội bộ"}), 500
    