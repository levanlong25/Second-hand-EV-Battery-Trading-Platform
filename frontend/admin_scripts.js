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
  loadAllTransactions();
  loadAllReports('pending');
  loadFeeConfig();  
  loadStatistics(); 
  const feeForm = document.getElementById('fees-form');
  if (feeForm && !feeForm._eventsAttached) {  
     feeForm.addEventListener("submit", handleFeeFormSubmit);
     feeForm._eventsAttached = true;
  }
}

// --- DATA LOADING & RENDERING ---
async function loadAllUsers() {
  try {
    const users = await apiRequest("/admin/admin/users");
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
                                <button onclick="showUserActivity(${user.user_id}, '${user.username}')" class="text-green-600 hover:text-green-900">Hoạt Động</button>
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
    const allListings = await apiRequest("/admin/admin/listings");
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
    const allAuctions = await apiRequest("/admin/admin/auctions");
    const pendingContainer = document.getElementById(
      "pending-auctions-container"
    );
    const allContainer = document.getElementById("all-auctions-container");

    let pendingHtml = "";
    let allHtml = "";

    if (allAuctions && Array.isArray(allAuctions)) {
      allAuctions.forEach((auction) => {
        let priceLabel = "Giá hiện tại:";
        let winnerDisplayHtml = "";

        if (auction.auction_status === "ended") {
          priceLabel = "Giá cuối cùng:";
          winnerDisplayHtml = ` | Người thắng: ${
            auction.winning_bidder_id ?? "Không có"
          }`;
        }
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
                                    } | Người thắng đấu giá: ${auction.winning_bidder_id} | Giá: ${
                                      auction.current_bid
                                    } | Trạng thái: 
                                        <span class="font-semibold ${
                                          auction.auction_status === "pending"
                                            ? "text-yellow-600"
                                            : auction.auction_status ===
                                              "prepare"
                                            ? "text-blue-600"
                                            : auction.auction_status ===
                                              "started"
                                            ? "text-red-600"
                                            : auction.auction_status === "ended"
                                            ? "text-green-600"
                                            : auction.auction_status ===
                                              "rejected"
                                            ? "text-gray-500 line-through"
                                            : "text-gray-700"
                                        }">${auction.auction_status}</span>
                                    </p>
                                    <p class="text-xs text-gray-500">
                                        Bắt đầu: ${new Date(
                                          auction.start_time
                                        ).toLocaleString("vi-VN")} | 
                                        Kết thúc: ${new Date(
                                          auction.end_time
                                        ).toLocaleString("vi-VN")}
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
                                    ${
                                      auction.auction_status === "started"
                                        ? `
                                            <button onclick="finalizeAuctionAction(${auction.auction_id})" class="bg-blue-500 text-white text-xs font-bold py-1 px-2 rounded hover:bg-blue-600" title="Hoàn tất thủ công">Kết thúc</button>
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
      await apiRequest(`/admin/admin/users/${userId}/toggle-lock`, "POST");
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
      await apiRequest(`/admin/admin/users/${userId}`, "DELETE");
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
        `/admin/admin/listings/${listingId}/status`,
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
      await apiRequest(`/admin/admin/listings/${listingId}`, "DELETE");
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
        `/admin/admin/auctions/${auctionId}/status`,
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
      await apiRequest(`/admin/admin/auctions/${auctionId}`, "DELETE");
      showToast("Xóa đấu giá thành công.");
      loadAllAuctions();
    } catch (error) {}
  }
}

async function reviewAuctionAction(auctionId, approve) {
    try { 
        await apiRequest(`/admin/admin/auctions/review`, 'POST', { auction_id: auctionId, approve: approve });
        showToast(`Đã ${approve ? 'duyệt' : 'từ chối'} đấu giá #${auctionId}.`);
        loadAllAuctions();
    } catch (error) { /*...*/ } finally {  }
}
 
async function finalizeAuctionAction(auctionId) {
     if (!confirm(`...`)) return;
    try { 
        await apiRequest(`/admin/admin/auctions/${auctionId}/finalize`, 'PUT');
        showToast(`Đã kết thúc đấu giá #${auctionId}.`);
        loadAllAuctions();
    } catch (error) { /*...*/ } finally {  }
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
    case "initiated":
      return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">Chờ thanh toán</span>';
    case "pending":
      return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Chờ duyệt</span>';
    case "completed":
      return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Hoàn thành</span>';
    case "failed":
      return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Thất bại</span>';
    default:
      return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">${status}</span>`;
  }
}

function formatAdminPaymentMethod(method) {
  switch (method) {
    case "e-wallet":
      return "Ví điện tử";
    case "bank":
      return "Ngân hàng";
    case "cash":
      return "Tiền mặt";
    default:
      return method || "N/A";
  }
}
async function loadAllTransactions() {
  try {
    // ASSUMPTION: API returns an array of objects like:
    // { transaction_id, payment_id, buyer_username, seller_username, amount, payment_method, payment_status }
    const payments = await apiRequest("/admin/admin/payments");
    const tbody = document.getElementById("transactions-table-body");

    if (payments && Array.isArray(payments)) {
      tbody.innerHTML = payments
        .map(
          (p) => `
                <tr>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${
                      p.transaction_id
                    }</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                      p.payment_id
                    }</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                      p.buyer_username || "N/A"
                    }</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${
                      p.seller_username || "N/A"
                    }</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">${parseFloat(
                      p.amount || 0
                    ).toLocaleString("vi-VN")} VNĐ</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${formatAdminPaymentMethod(
                      p.payment_method
                    )}</td>
                    <td class="px-6 py-4 whitespace-nowrap">${formatAdminPaymentStatus(
                      p.payment_status
                    )}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                        ${
                          p.payment_status === "pending"
                            ? `<button onclick="approvePayment(${p.payment_id})" class="text-indigo-600 hover:text-indigo-900 bg-indigo-100 hover:bg-indigo-200 px-3 py-1 rounded-md">Duyệt (Complete)</button>`
                            : `<span class="text-gray-400">${
                                p.payment_status === "completed"
                                  ? "Đã duyệt"
                                  : p.payment_status === "failed"
                                  ? "Thất bại"
                                  : "Chờ TT"
                              }</span>`
                        }
                    </td>
                </tr>
            `
        )
        .join("");
    } else {
      tbody.innerHTML =
        '<tr><td colspan="8" class="text-center py-4 text-gray-500">Không có giao dịch nào.</td></tr>';
    }
  } catch (error) {
    const tbody = document.getElementById("transactions-table-body");
    if (tbody)
      tbody.innerHTML =
        '<tr><td colspan="8" class="text-center py-4 text-red-500">Lỗi khi tải giao dịch.</td></tr>';
  }
}
async function approvePayment(paymentId) {
  if (
    confirm(
      `Bạn có chắc chắn muốn duyệt (chuyển sang 'completed') cho thanh toán ID ${paymentId}?`
    )
  ) {
    try {
      // ASSUMPTION: API expects a PUT/POST request to approve
      await apiRequest(
        `/admin/admin/payments/${paymentId}/approve`,
        "PUT"
      ); // Or 'POST' depending on your backend
      showToast("Duyệt thanh toán thành công.");
      loadAllTransactions(); // Refresh the transaction list
    } catch (error) {
      // Error toast is handled by apiRequest
    }
  }
}

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');  
    }
}
 
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
    }
}
 
function openUserModal() { 
    document.getElementById('user-form').reset(); 
    document.getElementById('user-modal-title').textContent = 'Thêm Người Dùng Mới'; 
    document.getElementById('user-password').required = true;
    document.getElementById('user-password').placeholder = 'Ít nhất 6 ký tự (bắt buộc)';

    openModal('user-modal');
}
 
document.getElementById("user-form").addEventListener("submit", async (e) => {
    e.preventDefault();
 
    const username = document.getElementById("user-username").value;
    const email = document.getElementById("user-email").value;
    const password = document.getElementById("user-password").value; 
    const role = document.getElementById("user-role").value;
    const status = document.getElementById("user-status").value;

    const body = {
        username: username,
        email: email,
        password: password, 
        role: role,
        status: status,
    };

    const endpoint = "/admin/admin/users"; 
    const method = "POST";

    try {
        await apiRequest(endpoint, method, body);
        showToast("Thêm người dùng thành công!");
        closeModal("user-modal");
        loadAllUsers(); 
    } catch (error) {
        console.error("Lỗi khi thêm người dùng:", error);
    }
});
function showUserActivity(userId, username) { 
    document
        .querySelectorAll(".dashboard-section")
        .forEach((section) => section.classList.remove("active")); 
    document.getElementById("user-activity-section").classList.add("active");
 
    document.getElementById(
      "activity-username"
    ).textContent = `${username} (ID: ${userId})`;
 
    loadReviewsByReviewer(userId);
    loadReportsByReporter(userId);
}
 
async function loadReviewsByReviewer(userId) {
    const container = document.getElementById("user-reviews-list");
    container.innerHTML = '<p class="text-gray-500">Đang tải đánh giá...</p>';
    try { 
        const reviews = await apiRequest(`/admin/admin/reviews/by-user/${userId}`);
        renderUserReviews(reviews, container);
    } catch (error) {
        console.error(`Lỗi tải reviews cho user ${userId}:`, error);
        container.innerHTML =
          '<p class="text-red-500">Không thể tải danh sách đánh giá.</p>';
    }
}
 
async function loadReportsByReporter(userId) {
    const container = document.getElementById("user-reports-list");
    container.innerHTML = '<p class="text-gray-500">Đang tải báo cáo...</p>';
    try { 
        const reports = await apiRequest(`/admin/admin/reports/by-user/${userId}`);
        renderUserReports(reports, container);
    } catch (error) {
        console.error(`Lỗi tải reports cho user ${userId}:`, error);
        container.innerHTML =
          '<p class="text-red-500">Không thể tải danh sách báo cáo.</p>';
    }
}
 
function renderUserReviews(reviews, container) {
    if (!reviews || !Array.isArray(reviews) || reviews.length === 0) {
        container.innerHTML =
          "<p class='text-gray-500'>Người dùng này chưa viết đánh giá nào.</p>";
        return;
    }
    container.innerHTML = reviews
        .map(
            (r) => `
          <div class="border p-3 rounded-lg bg-gray-50">
              <p class="text-sm text-gray-500">Giao dịch #${
                r.transaction_id
              } (Đánh giá User ID: ${r.reviewed_user_id})</p>
              <p class="font-semibold text-lg text-yellow-500">${"⭐".repeat(
                r.rating
              )}</p>
              <p class="italic my-2">"${r.comment}"</p>
              <p class="text-xs text-gray-400">Ngày: ${new Date(
                r.created_at
              ).toLocaleDateString("vi-VN")}</p>
          </div>
      `
        )
        .join("");
}
 
function renderUserReports(reports, container) {
    if (!reports || !Array.isArray(reports) || reports.length === 0) {
        container.innerHTML =
          "<p class='text-gray-500'>Người dùng này chưa gửi báo cáo nào.</p>";
        return;
    }
    container.innerHTML = reports
        .map(
            (r) => `
          <div class="border p-3 rounded-lg bg-red-50 border-red-200">
              <p class="text-sm text-gray-500">Giao dịch #${
                r.transaction_id
              } (Báo cáo User ID: ${r.reported_user_id})</p>
              <p class="font-semibold text-red-700">Lý do: ${r.reason}</p>
              <p class="italic my-2">"${r.details}"</p>
              <p class="text-sm font-semibold capitalize">Trạng thái: ${r.status}</p>
              <p class="text-xs text-gray-400">Ngày: ${new Date(
                r.created_at
              ).toLocaleDateString("vi-VN")}</p>
          </div>
      `
        )
        .join("");
}
async function loadAllReports(statusFilter) {
    const tbody = document.getElementById("reports-table-body");
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-gray-500">Đang tải danh sách báo cáo...</td></tr>';
    try {
        let endpoint = "/admin/admin/reports";  
        if (statusFilter) {
            endpoint += `?status=${statusFilter}`;
        }
        const reports = await apiRequest(endpoint);

        if (reports && Array.isArray(reports) && reports.length > 0) {
            tbody.innerHTML = reports.map(r => `
                <tr class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">${r.report_id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${r.transaction_id}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${r.reporter_username || `ID: ${r.reporter_id}`}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${r.reported_username || `ID: ${r.reported_user_id}`}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-semibold text-red-600">${r.reason}</td>
                    <td class="px-6 py-4 text-sm text-gray-700 max-w-xs truncate" title="${r.details || ''}">${r.details || 'N/A'}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">${formatAdminReportStatus(r.status)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-center text-sm font-medium space-x-2">
                        ${
                            r.status === 'pending' ? `
                                <button onclick="handleReportAction(${r.report_id}, 'resolved')" class="text-green-600 hover:text-green-900 bg-green-100 hover:bg-green-200 px-3 py-1 rounded-md text-xs font-bold">Giải quyết</button>
                                <button onclick="handleReportAction(${r.report_id}, 'dismissed')" class="text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded-md text-xs font-bold">Bỏ qua</button>
                            ` : `
                                <span class="text-gray-400 text-xs italic">Đã xử lý</span>
                            `
                        }
                    </td>
                </tr>
            `).join("");
        } else {
            tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-gray-500">Không có báo cáo nào.</td></tr>';
        }
    } catch (error) {
        console.error("Lỗi khi tải báo cáo:", error);
        tbody.innerHTML = '<tr><td colspan="8" class="text-center py-4 text-red-500">Lỗi khi tải danh sách báo cáo.</td></tr>';

  } finally {
  }
    
    document.querySelectorAll('.report-tab-filter').forEach(tab => {
        tab.classList.remove('border-indigo-500', 'text-indigo-600');
        tab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700');
    }); 
    const selector = `button[onclick="loadAllReports(${statusFilter === null ? 'null' : `'${statusFilter}'`})"]`;
    const activeTab = document.querySelector(selector);
    if(activeTab) {
        activeTab.classList.add('border-indigo-500', 'text-indigo-600');
        activeTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700');
    }
}
 
async function handleReportAction(reportId, newStatus) {
    const actionText = newStatus === 'resolved' ? 'Giải quyết' : 'Bỏ qua';
    if (!confirm(`Bạn có chắc muốn '${actionText}' báo cáo ID ${reportId}?`)) return;
    try {
        await apiRequest(
            `/admin/admin/reports/${reportId}/status`,  
            "PUT",
            { status: newStatus }
        );
        showToast(`Đã cập nhật trạng thái báo cáo #${reportId}.`);
         
        const activeTab = document.querySelector('.report-tab-filter.border-indigo-500');
        let currentFilter = null;
        if (activeTab) { 
            const onclickAttr = activeTab.getAttribute('onclick');  
            const match = onclickAttr.match(/loadAllReports\((.*?)\)/);
            if (match && match[1] !== 'null') {
                currentFilter = match[1].replace(/'/g, '');  
            }
        }
        loadAllReports(currentFilter);  
    } catch (error) { 
    } finally {}
}

function formatAdminReportStatus(status) {
    switch (status) {
        case "pending":
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">Chờ xử lý</span>';
        case "resolved":
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Đã giải quyết</span>';
        case "dismissed":
            return '<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">Đã bỏ qua</span>';
        default:
            return `<span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">${status}</span>`;
    }
}


// Biến toàn cục để giữ instance của biểu đồ
let myRevenueChart = null;

/**
 * Tải tất cả dữ liệu thống kê (KPIs và Biểu đồ)
 */
async function loadStatistics() {
    document.getElementById('stats-total-revenue').textContent = 'Đang tải...';
    document.getElementById('stats-total-transactions').textContent = 'Đang tải...';
    document.getElementById('stats-pending-payments').textContent = 'Đang tải...';
    document.getElementById('chart-loading').classList.remove('hidden');
    document.getElementById('chart-container').classList.add('hidden');

    try {
        const [kpiData, trendData] = await Promise.all([
            apiRequest("/admin/admin/stats/kpis"),
            apiRequest("/admin/admin/stats/revenue-trend")
        ]);

        renderKpiCards(kpiData);
        renderRevenueChart(trendData);
    } catch (error) {
        console.error("Lỗi khi tải dữ liệu thống kê:", error);
        showToast("Không thể tải dữ liệu thống kê.", "error");
        document.getElementById('chart-loading').innerHTML =
            '<p class="text-red-500">Lỗi tải dữ liệu biểu đồ.</p>';
    }
}

/**
 * Điền dữ liệu vào các thẻ KPI
 */
function renderKpiCards(kpis) {
    if (!kpis) return;

    const revenueFormatted = new Intl.NumberFormat("vi-VN", {
        style: "currency",
        currency: "VND",
        maximumFractionDigits: 0
    }).format(kpis.total_revenue || 0);

    document.getElementById('stats-total-revenue').textContent = revenueFormatted;
    document.getElementById('stats-total-transactions').textContent = kpis.total_transactions || 0;
    document.getElementById('stats-pending-payments').textContent = kpis.pending_payments || 0;
}

/**
 * Vẽ biểu đồ doanh thu bằng Chart.js
 */
function renderRevenueChart(trendData) {
    const ctx = document.getElementById('revenue-chart');
    if (!ctx) return;

    const chartContainer = document.getElementById('chart-container');
    const loadingContainer = document.getElementById('chart-loading');

    if (!trendData || !Array.isArray(trendData) || trendData.length === 0) {
        loadingContainer.innerHTML = '<p class="text-gray-500">Không có dữ liệu xu hướng doanh thu trong 30 ngày qua.</p>';
        loadingContainer.classList.remove('hidden');
        chartContainer.classList.add('hidden');
        return;
    }

    if (myRevenueChart) {
        myRevenueChart.destroy();
    }

    const labels = trendData.map(item => {
        const parts = item.date.split('-');
        return `${parts[2]}/${parts[1]}`;
    });
    const dataPoints = trendData.map(item => item.total);

    const config = {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Doanh thu (VNĐ)',
                data: dataPoints,
                fill: true,
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderColor: 'rgba(79, 70, 229, 1)',
                tension: 0.3,
                pointBackgroundColor: 'rgba(79, 70, 229, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function (value) {
                            if (value >= 1000000) return (value / 1000000) + ' Tr';
                            if (value >= 1000) return (value / 1000) + ' k';
                            return value;
                        }
                    }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.dataset.label || '';
                            if (label) label += ': ';
                            if (context.parsed.y !== null) {
                                label += new Intl.NumberFormat('vi-VN', {
                                    style: 'currency',
                                    currency: 'VND'
                                }).format(context.parsed.y);
                            }
                            return label;
                        }
                    }
                }
            }
        }
    };

    myRevenueChart = new Chart(ctx, config);

    chartContainer.classList.remove('hidden');
    loadingContainer.classList.add('hidden');
}

async function loadFeeConfig() {
  const form = document.getElementById('fees-form');
  if (!form) return; // Chỉ chạy nếu đang ở trang có form

  const listRateInput = document.getElementById('listing-fee-rate');
  const auctionRateInput = document.getElementById('auction-fee-rate');

  try {
    // Gọi API admin-service
    const config = await apiRequest("/admin/admin/fees", "GET");

    if (config && config.listing_fee_rate !== undefined) {
      listRateInput.value = config.listing_fee_rate;
      auctionRateInput.value = config.auction_fee_rate;
    } else {
      throw new Error("Không nhận được dữ liệu cấu hình phí.");
    }

  } catch (error) {
    console.error("Lỗi khi tải cấu hình phí:", error);
    // apiRequest đã hiển thị toast lỗi
    listRateInput.value = 'Lỗi';
    auctionRateInput.value = 'Lỗi';
  } finally {}
}

/**
 * Xử lý sự kiện submit form cấu hình phí
 */
async function handleFeeFormSubmit(event) {
  event.preventDefault();

  const submitButton = document.querySelector("#fees-form button[type='submit']");
  submitButton.disabled = true;
  submitButton.textContent = 'Đang lưu...';

  try {
    const listingRate = parseFloat(document.getElementById('listing-fee-rate').value);
    const auctionRate = parseFloat(document.getElementById('auction-fee-rate').value);

    if (isNaN(listingRate) || isNaN(auctionRate) || listingRate < 0 || auctionRate < 0) {
      throw new Error("Vui lòng nhập tỷ lệ phí hợp lệ (là số không âm).");
    }

    const body = {
      listing_fee_rate: listingRate,
      auction_fee_rate: auctionRate
    };

    // Gọi API cập nhật
    const result = await apiRequest("/admin/admin/fees", "PUT", body);

    showToast(result.message || "Cập nhật phí thành công!");

    // Cập nhật lại input (chuẩn hóa format)
    if (result.fee_config) {
      document.getElementById('listing-fee-rate').value = result.fee_config.listing_fee_rate;
      document.getElementById('auction-fee-rate').value = result.fee_config.auction_fee_rate;
    }

  } catch (error) {
    console.error("Lỗi khi cập nhật phí:", error);
    // apiRequest đã hiển thị toast lỗi
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Lưu Cấu hình Phí';
  }
}
