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
