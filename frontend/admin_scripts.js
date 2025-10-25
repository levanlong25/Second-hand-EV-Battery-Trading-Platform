const apiBaseUrl = "http://localhost";
const loginPage = document.getElementById("admin-login-page");
const dashboardPage = document.getElementById("dashboard");

// --- UTILITY FUNCTIONS ---
const showToast = (message, isError = false) => {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.className = `fixed bottom-5 right-5 p-4 rounded-lg shadow-lg text-white ${
    isError ? "bg-red-500" : "bg-green-500"
  } z-50`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
};

async function apiRequest(endpoint, method = "GET", body = null) {
  try {
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("admin_jwt_token");
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    const options = { method, headers };
    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(`${apiBaseUrl}${endpoint}`, options);
    const responseData = await response
      .json()
      .catch(() => ({ message: "Operation successful" }));

    if (!response.ok) {
      throw new Error(
        responseData.error ||
          responseData.msg ||
          `HTTP error! status: ${response.status}`
      );
    }
    return responseData;
  } catch (error) {
    console.error("API Request Error:", error);
    showToast(error.message, true);
    throw error;
  }
}

// --- DASHBOARD NAVIGATION ---
function showSection(sectionId) {
  document
    .querySelectorAll(".dashboard-section")
    .forEach((section) => section.classList.remove("active"));
  document.getElementById(sectionId).classList.add("active");

  document.querySelectorAll(".tab-link").forEach((link) => {
    link.classList.remove("border-indigo-500", "text-indigo-600");
    link.classList.add(
      "border-transparent",
      "text-gray-500",
      "hover:text-gray-700",
      "hover:border-gray-300"
    );
  });
  const activeLink = document.querySelector(
    `a[onclick="showSection('${sectionId}')"]`
  );
  activeLink.classList.add("border-indigo-500", "text-indigo-600");
  activeLink.classList.remove("border-transparent", "text-gray-500");
}

// --- AUTHENTICATION ---
document
  .getElementById("admin-login-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const email_username = document.getElementById("admin-email").value;
    const password = document.getElementById("admin-password").value;
    try {
      const data = await apiRequest("/user/api/login", "POST", {
        email_username,
        password,
      });
      const token = data.access_token;
      const payload = JSON.parse(atob(token.split(".")[1]));
      if (payload.role !== "admin") {
        throw new Error("Bạn không có quyền truy cập trang quản trị.");
      }
      localStorage.setItem("admin_jwt_token", token);
      showToast("Đăng nhập quản trị thành công!");
      showDashboard();
    } catch (error) {}
  });

function adminLogout() {
  localStorage.removeItem("admin_jwt_token");
  showToast("Bạn đã đăng xuất.");
  loginPage.style.display = "flex";
  dashboardPage.style.display = "none";
}

function showDashboard() {
  loginPage.style.display = "none";
  dashboardPage.style.display = "block";
  showSection("users-section");
  loadAllUsers();
  loadAllListings();
  loadAllAuctions();
  loadAllTransactions()
}

// --- DATA LOADING & RENDERING ---
async function loadAllUsers() {
  try {
    const users = await apiRequest("/user/api/admin/users");
    const tbody = document.getElementById("users-table-body");
    if (users && Array.isArray(users)) {
      tbody.innerHTML = users
        .map(
          (user) => `
                        <tr>
                            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${
                              user.user_id
                            }</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                              user.username
                            }</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                              user.email
                            }</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                              user.role
                            }</td>
                            <td class="px-6 py-4 whitespace-nowrap text-sm">
                                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                                  user.status === "active"
                                    ? "bg-green-100 text-green-800"
                                    : "bg-red-100 text-red-800"
                                }">
                                    ${user.status}
                                </span>
                            </td>
                            <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium space-x-2">
                                <button onclick="toggleUserLock(${
                                  user.user_id
                                })" class="text-indigo-600 hover:text-indigo-900">
                                    ${
                                      user.status === "active"
                                        ? "Lock"
                                        : "Unlock"
                                    }
                                </button>
                                <button onclick="deleteUser(${
                                  user.user_id
                                })" class="text-red-600 hover:text-red-900">Delete</button>
                            </td>
                        </tr>
                    `
        )
        .join("");
    }
  } catch (error) {}
}

// SỬA LỖI: Hoàn thiện hàm này
async function loadAllListings() {
  try {
    const allListings = await apiRequest("/listing/api/admin/all-listings");
    const pendingContainer = document.getElementById(
      "pending-listings-container"
    );
    const allContainer = document.getElementById("all-listings-container");

    let pendingHtml = "";
    let allHtml = "";

    if (allListings && Array.isArray(allListings)) {
      allListings.forEach((listing) => {
        const listingCardHtml = `
                            <div class="bg-white p-4 rounded-lg shadow flex justify-between items-center">
                                <div>
                                    <p class="font-bold">${
                                      listing.title
                                    } <span class="text-sm font-normal text-gray-500">(${
          listing.listing_type
        })</span></p>
                                    <p class="text-sm text-gray-600">ID: ${
                                      listing.listing_id
                                    } | Người bán: ${
          listing.seller_id
        } | Trạng thái: 
                                        <span class="font-semibold ${
                                          listing.status === "pending"
                                            ? "text-yellow-600"
                                            : "text-gray-700"
                                        }">${listing.status}</span>
                                    </p>
                                </div>
                                <div class="space-x-2">
                                    ${
                                      listing.status === "pending"
                                        ? `
                                        <button onclick="updateListingStatus(${listing.listing_id}, 'available')" class="bg-green-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-green-600">Duyệt</button>
                                        <button onclick="updateListingStatus(${listing.listing_id}, 'rejected')" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Từ chối</button>
                                    `
                                        : ""
                                    }
                                    <button onclick="deleteListing(${
                                      listing.listing_id
                                    })" class="text-gray-500 hover:text-red-600 text-sm font-bold py-1 px-3">Xóa</button>
                                </div>
                            </div>
                        `;

        if (listing.status === "pending") {
          pendingHtml += listingCardHtml;
        }
        allHtml += listingCardHtml;
      });
    }

    pendingContainer.innerHTML =
      pendingHtml ||
      '<p class="text-gray-500">Không có tin đăng nào chờ duyệt.</p>';
    allContainer.innerHTML =
      allHtml ||
      '<p class="text-gray-500">Chưa có tin đăng nào trong hệ thống.</p>';
  } catch (error) {}
}

async function loadAllAuctions() {
  try {
    const allAuctions = await apiRequest("/auction/api/admin/all-auctions");
    const pendingContainer = document.getElementById(
      "pending-auctions-container"
    );
    const allContainer = document.getElementById("all-auctions-container");

    let pendingHtml = "";
    let allHtml = "";

    if (allAuctions && Array.isArray(allAuctions)) {
      allAuctions.forEach((auction) => {
        const auctionCardHtml = `
                            <div class="bg-white p-4 rounded-lg shadow flex justify-between items-center">
                                <div>
                                    <p class="font-bold"> <span class="text-sm font-normal text-gray-500">Loại: ${
          auction.auction_type
        }</span></p>
                                    <p class="text-sm text-gray-600">ID: ${
                                      auction.auction_id
                                    } | Người tạo đấu giá: ${
          auction.bidder_id
        } | Trạng thái: 
                                        <span class="font-semibold ${
                                          auction.auction_status === "pending"
                                            ? "text-yellow-600"
                                            : "text-gray-700"
                                        }">${auction.auction_status}</span>
                                    </p>
                                </div>
                                <div class="space-x-2">
                                    ${
                                      auction.auction_status === "pending"
                                        ? `
                                        <button onclick="updateAuctionStatus(${auction.auction_id}, 'prepare')" class="bg-green-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-green-600">Duyệt</button>
                                        <button onclick="updateAuctionStatus(${auction.auction_id}, 'rejected')" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Từ chối</button>
                                    `
                                        : ""
                                    }
                                    <button onclick="deleteAuction(${
                                      auction.auction_id
                                    })" class="text-gray-500 hover:text-red-600 text-sm font-bold py-1 px-3">Xóa</button>
                                </div>
                            </div>
                        `;

        if (auction.auction_status === "pending") {
          pendingHtml += auctionCardHtml;
        }
        allHtml += auctionCardHtml;
      });
    }

    pendingContainer.innerHTML =
      pendingHtml ||
      '<p class="text-gray-500">Không có đấu giá nào chờ duyệt.</p>';
    allContainer.innerHTML =
      allHtml ||
      '<p class="text-gray-500">Chưa có đấu giá nào trong hệ thống.</p>';
  } catch (error) {}
}


// --- ACTION HANDLERS ---
async function toggleUserLock(userId) {
  if (
    confirm("Bạn có chắc chắn muốn thay đổi trạng thái của người dùng này?")
  ) {
    try {
      await apiRequest(`/user/api/admin/users/${userId}/toggle-lock`, "POST");
      showToast("Cập nhật trạng thái thành công.");
      loadAllUsers();
    } catch (error) {}
  }
}

async function deleteUser(userId) {
  if (
    confirm("CẢNH BÁO: Bạn có chắc chắn muốn XÓA VĨNH VIỄN người dùng này?")
  ) {
    try {
      await apiRequest(`/user/api/admin/users/${userId}`, "DELETE");
      showToast("Xóa người dùng thành công.");
      loadAllUsers();
    } catch (error) {}
  }
}

async function updateListingStatus(listingId, newStatus) {
  const action = newStatus === "available" ? "duyệt" : "từ chối";
  if (confirm(`Bạn có chắc chắn muốn ${action} tin đăng này?`)) {
    try {
      await apiRequest(
        `/listing/api/admin/listings/${listingId}/status`,
        "PUT",
        { status: newStatus }
      );
      showToast("Cập nhật trạng thái tin đăng thành công.");
      loadAllListings(); // Refresh both lists
    } catch (error) {}
  }
}

async function deleteListing(listingId) {
  if (confirm("CẢNH BÁO: Bạn có chắc chắn muốn XÓA VĨNH VIỄN tin đăng này?")) {
    try {
      // Endpoint này thuộc listing_controller
      await apiRequest(`/listing/api/listings/${listingId}`, "DELETE");
      showToast("Xóa tin đăng thành công.");
      loadAllListings();
    } catch (error) {}
  }
}

async function updateAuctionStatus(auctionId, newStatus) {
  const action = newStatus === "prepare" ? "duyệt" : "từ chối";
  if (confirm(`Bạn có chắc chắn muốn ${action} đấu giá này?`)) {
    try {
      await apiRequest(
        `/auction/api/admin/auctions/${auctionId}/auction_status`,
        "PUT",
        { auction_status: newStatus }
      );
      showToast("Cập nhật trạng thái đấu giá thành công.");
      loadAllAuctions();  
    } catch (error) {}
  }
}

async function deleteAuction(auctionId) {
  if (confirm("CẢNH BÁO: Bạn có chắc chắn muốn XÓA VĨNH VIỄN auction này?")) {
    try { 
      await apiRequest(`/auction/api/auctions/${auctionId}`, "DELETE");
      showToast("Xóa đấu giá thành công.");
      loadAllAuctions();
    } catch (error) {}
  }
}


// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  const token = localStorage.getItem("admin_jwt_token");
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      if (payload.role === "admin" && payload.exp * 1000 > Date.now()) {
        showDashboard();
      } else {
        adminLogout();
      }
    } catch (e) {
      adminLogout();
    }
  } else {
    loginPage.style.display = "flex";
    dashboardPage.style.display = "none";
  }
});
function formatAdminPaymentStatus(status) {
    switch (status) {
        case 'initiated':
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Chờ thanh toán</span>';
        case 'pending':
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Chờ duyệt</span>';
        case 'completed':
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Hoàn thành</span>';
        case 'failed':
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Thất bại</span>';
        default:
            return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">${status}</span>`;
    }
}

function formatAdminPaymentMethod(method) {
    switch (method) {
        case 'e-wallet': return 'Ví điện tử';
        case 'bank': return 'Ngân hàng';
        case 'cash': return 'Tiền mặt';
        default: return method || 'N/A';
    }
}
async function loadAllTransactions() {
    try {
        // ASSUMPTION: API returns an array of objects like:
        // { transaction_id, payment_id, buyer_username, seller_username, amount, payment_method, payment_status }
        const payments = await apiRequest("/transaction/api/admin/all-payments");
        const tbody = document.getElementById("transactions-table-body");

        if (payments && Array.isArray(payments)) {
            tbody.innerHTML = payments.map(p => `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${p.transaction_id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${p.payment_id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${p.buyer_username || 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${p.seller_username || 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${parseFloat(p.amount || 0).toLocaleString('vi-VN')} VNĐ</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatAdminPaymentMethod(p.payment_method)}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${formatAdminPaymentStatus(p.payment_status)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                        ${p.payment_status === 'pending'
                            ? `<button onclick="approvePayment(${p.payment_id})" class="text-indigo-600 hover:text-indigo-900 bg-indigo-100 hover:bg-indigo-200 px-3 py-1 rounded-md">Duyệt (Complete)</button>`
                            : `<span class="text-gray-400">${p.payment_status === 'completed' ? 'Đã duyệt' : (p.payment_status === 'failed' ? 'Thất bại' : 'Chờ TT')}</span>`
                        }
                    </td>
                </tr>
            `).join("");
        } else {
             tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-gray-500">Không có giao dịch nào.</td></tr>';
        }
    } catch (error) {
         const tbody = document.getElementById("transactions-table-body");
         if (tbody) tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-red-500">Lỗi khi tải giao dịch.</td></tr>';
    }
}
async function approvePayment(paymentId) {
    if (confirm(`Bạn có chắc chắn muốn duyệt (chuyển sang 'completed') cho thanh toán ID ${paymentId}?`)) {
        try {
            // ASSUMPTION: API expects a PUT/POST request to approve
            await apiRequest(`/transaction/api/admin/payments/${paymentId}/approve`, 'PUT'); // Or 'POST' depending on your backend
            showToast("Duyệt thanh toán thành công.");
            loadAllTransactions(); // Refresh the transaction list
        } catch (error) {
            // Error toast is handled by apiRequest
        }
    }
}