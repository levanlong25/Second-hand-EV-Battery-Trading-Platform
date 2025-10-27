// =================================================================
// PART 1: CONFIGURATION & GENERAL UTILITIES
// =================================================================

const apiBaseUrl = "http://localhost";

// --- DOM ELEMENTS ---
const navAuthLinks = document.getElementById("nav-auth-links");
const loadingSpinner = document.getElementById("loading-spinner");

// --- GENERAL UTILITY FUNCTIONS ---

/** Hiển thị spinner loading */
const showLoading = () => loadingSpinner.classList.remove("hidden");

/** Ẩn spinner loading */
const hideLoading = () => loadingSpinner.classList.add("hidden");

const showToast = (message, isError = false) => {
  const toast = document.createElement("div");
  toast.textContent = message;
  toast.className = `fixed bottom-5 right-5 p-4 rounded-lg shadow-lg text-white ${
    isError ? "bg-red-500" : "bg-green-500"
  } z-50`;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
};

function closeAdd(id) {
  document.getElementById(id).classList.add("hidden");
}

const closeModal = (modalId) =>
  document.getElementById(modalId).classList.remove("active");

const openModal = (modalId, data = {}) => {
  const modal = document.getElementById(modalId);
  if (!modal) {
    console.error(`Modal with id "${modalId}" not found.`);
    return;
  }
  const form = modal.querySelector("form");
  if (form) {
    form.reset();
    if (modalId === "vehicle-modal") {
      document.getElementById("vehicle-modal-title").textContent =
        data.vehicle_id ? "Sửa thông tin Xe" : "Thêm Xe Mới";
      document.getElementById("vehicle-id").value = data.vehicle_id || "";
      document.getElementById("vehicle-brand").value = data.brand || "";
      document.getElementById("vehicle-model").value = data.model || "";
      document.getElementById("vehicle-year").value = data.year || "";
      document.getElementById("vehicle-mileage").value = data.mileage || "";
    } else if (modalId === "battery-modal") {
      document.getElementById("battery-modal-title").textContent =
        data.battery_id ? "Sửa thông tin Pin" : "Thêm Pin Mới";
      document.getElementById("battery-id").value = data.battery_id || "";
      document.getElementById("battery-manufacturer").value =
        data.manufacturer || "";
      document.getElementById("battery-capacity").value =
        data.capacity_kwh || "";
      document.getElementById("battery-health").value =
        data.health_percent || "";
    } else if (modalId === "listing-modal") {
      document.getElementById("listing-item-id").value = data.id || "";
      document.getElementById("listing-item-type").value = data.type || "";
    } else if (modalId === "auction-modal") {
      document.getElementById("auction-item-id").value = data.id || "";
      document.getElementById("auction-item-type").value = data.type || "";

      // Tự động đặt thời gian bắt đầu mặc định là 2 giờ kể từ bây giờ
      const defaultStartTime = new Date(Date.now() + 2 * 60 * 60 * 1000);
      const y = defaultStartTime.getFullYear();
      const m = (defaultStartTime.getMonth() + 1).toString().padStart(2, "0");
      const d = defaultStartTime.getDate().toString().padStart(2, "0");
      const h = defaultStartTime.getHours().toString().padStart(2, "0");
      const min = defaultStartTime.getMinutes().toString().padStart(2, "0");
      const formattedStartTime = `${y}-${m}-${d}T${h}:${min}`;
      document.getElementById("auction-start-time").value = formattedStartTime;
    }
  }
  modal.classList.add("active");
};

function renderStatusBadge(status) {
  if (!status) return "";

  const statusMap = {
    pending: { text: "Chờ duyệt", color: "bg-yellow-100 text-yellow-800" },
    available: { text: "Đang bán", color: "bg-green-100 text-green-800" },
    rejected: { text: "Bị từ chối", color: "bg-red-100 text-red-800" },
    sold: { text: "Đã bán", color: "bg-gray-100 text-gray-800" },
  };

  const statusInfo = statusMap[status] || {
    text: status,
    color: "bg-gray-100 text-gray-800",
  };

  return `<span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusInfo.color}">${statusInfo.text}</span>`;
}
//'pending', 'prepare','started', 'ended', 'rejected'
function renderStatusAuction(status) {
  if (!status) return "";

  const statusMap = {
    pending: { text: "Chờ duyệt", color: "bg-yellow-100 text-yellow-800" },
    prepare: { text: "Đã duyệt", color: "bg-green-100 text-green-800" },
    started: { text: "Đang đấu giá", color: "bg-red-100 text-red-800" },
    ended: { text: "Đã xong", color: "bg-gray-100 text-gray-800" },
    rejected: { text: "Bị từ chối", color: "bg-gray-100 text-gray-800" },
    error: { text: "Lỗi", color: "bg-red-100 text-red-800" },
    unknown_type: { text: "Không rõ", color: "bg-gray-100 text-gray-800" },
  };

  const statusInfo = statusMap[status] || {
    text: status,
    color: "bg-gray-100 text-gray-800",
  };

  return `<span class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${statusInfo.color}">${statusInfo.text}</span>`;
}

function isLoggedIn() {
  return !!localStorage.getItem("jwt_token");
}
// =================================================================
// PART 2: API & PAGE NAVIGATION
// =================================================================

async function apiRequest(endpoint, method = "GET", body = null) {
  showLoading();
  try {
    const headers = { "Content-Type": "application/json" };
    const token = localStorage.getItem("jwt_token");
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
  } finally {
    hideLoading();
  }
}

function navigateTo(pageId) {
  document
    .querySelectorAll(".page")
    .forEach((page) => page.classList.remove("active"));
  const targetPage = document.getElementById(`${pageId}-page`);
  if (targetPage) {
    targetPage.classList.add("active");
  } else {
    document.getElementById("home-page").classList.add("active");
  }

  // Tải dữ liệu tương ứng với trang
  if (pageId === "profile") {
    loadProfile();
    loadMyAssets();
  }
  if (pageId === "watchlist") {
    loadMyWatchlist();
  }
  if (pageId === "transactions") {
    loadMyTransactions();
  }
  if (pageId === "payment-result") {
    loadPaymentResult();
  }
  if (pageId === "pending-payments") {
    loadPaymentSections();
  }
  if (pageId === "reviews-reports") {
        loadMyReviewsAndReports();
    }
  if (pageId === "listings") {
    loadPublicListings();
    loadPublicAuctions();
    showMarketTab("listings");
  }
}
// =================================================================
// PART 3: AUTHENTICATION & USER PROFILE
// =================================================================

/** Cập nhật các liên kết điều hướng dựa trên trạng thái đăng nhập. */
function updateNav() {
  const token = localStorage.getItem("jwt_token");
  if (token) {
    navAuthLinks.innerHTML = `
      <a href="#" onclick="navigateTo('profile')" class="nav-link text-gray-600 hover:bg-indigo-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Hồ Sơ & Kho</a>
      <a href="#" onclick="logout()" class="ml-4 bg-red-500 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-red-600">Đăng Xuất</a>
    `;
  } else {
    navAuthLinks.innerHTML = `
      <a href="#" onclick="navigateTo('login')" class="nav-link text-gray-600 hover:bg-indigo-600 hover:text-white px-3 py-2 rounded-md text-sm font-medium">Đăng Nhập</a>
      <a href="#" onclick="navigateTo('register')" class="ml-4 bg-green-500 text-white px-3 py-2 rounded-md text-sm font-medium hover:bg-green-600">Đăng Ký</a>
    `;
  }
}

/** Xử lý đăng xuất người dùng. */
function logout() {
  localStorage.removeItem("jwt_token");
  showToast("Bạn đã đăng xuất thành công.");
  updateNav();
  navigateTo("login");
}

/** Tải và hiển thị thông tin hồ sơ người dùng. */
async function loadProfile() {
  try {
    const data = await apiRequest("/user/api/profile");
    if (data) {
      // Hiển thị thông tin
      const detailsDiv = document.getElementById("profile-details");
      detailsDiv.innerHTML = `
        <p><strong>Họ và tên:</strong> ${data.full_name || "Chưa cập nhật"}</p>
        <p><strong>Điện thoại:</strong> ${
          data.phone_number || "Chưa cập nhật"
        }</p>
        <p><strong>Địa chỉ:</strong> ${data.address || "Chưa cập nhật"}</p>
      `;

      // Điền vào form cập nhật
      document.getElementById("profile-fullname").value = data.full_name || "";
      document.getElementById("profile-phone").value = data.phone_number || "";
      document.getElementById("profile-address").value = data.address || "";

      // Đảm bảo form được ẩn khi tải trang
      toggleProfileForm(false);
    }
  } catch (error) {
    console.error("Failed to load profile:", error);
  }
}

function toggleProfileForm(forceShow) {
  const form = document.getElementById("profile-update-form");
  const buttonContainer = document.getElementById(
    "update-profile-button-container"
  );

  if (!form || !buttonContainer) return;

  if (forceShow === true) {
    form.classList.remove("hidden");
    buttonContainer.classList.add("hidden");
  } else if (forceShow === false) {
    form.classList.add("hidden");
    buttonContainer.classList.remove("hidden");
  } else {
    form.classList.toggle("hidden");
    buttonContainer.classList.toggle("hidden");
  }
}

// --- AUTH & PROFILE EVENT LISTENERS ---

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email_username = document.getElementById("login-email-username").value;
  const password = document.getElementById("login-password").value;
  try {
    const data = await apiRequest("/user/api/login", "POST", {
      email_username,
      password,
    });
    if (data && data.access_token) {
      localStorage.setItem("jwt_token", data.access_token);
      showToast("Đăng nhập thành công!");
      updateNav();
      navigateTo("profile");
    } else {
      showToast("Đăng nhập thất bại. Vui lòng thử lại.", true);
    }
  } catch (error) {}
});

document
  .getElementById("register-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("register-username").value;
    const email = document.getElementById("register-email").value;
    const password = document.getElementById("register-password").value;
    try {
      const data = await apiRequest("/user/api/register", "POST", {
        username,
        email,
        password,
      });
      if (data) {
        showToast(data.message || "Đăng ký thành công! Vui lòng đăng nhập.");
        navigateTo("login");
      }
    } catch (error) {}
  });

document
  .getElementById("forget-password-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forget-email").value;
    try {
      const data = await apiRequest("/user/api/send-otp", "POST", { email });
      if (data) {
        showToast(data.message || "OTP đã được gửi đến email của bạn.");
        document.getElementById("forget-password-form").classList.add("hidden");
        document
          .getElementById("reset-password-form")
          .classList.remove("hidden");
      }
    } catch (error) {}
  });

document
  .getElementById("reset-password-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forget-email").value;
    const otp = document.getElementById("otp-code").value;
    const new_password = document.getElementById("new-password").value;
    try {
      const data = await apiRequest("/user/api/reset-password", "POST", {
        email,
        otp,
        new_password,
      });
      if (data) {
        showToast(data.message || "Mật khẩu đã được đặt lại thành công!");
        navigateTo("login");
      }
    } catch (error) {}
  });

document
  .getElementById("profile-update-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const body = {
      full_name: document.getElementById("profile-fullname").value,
      phone_number: document.getElementById("profile-phone").value,
      address: document.getElementById("profile-address").value,
    };
    try {
      await apiRequest("/user/api/profile", "PUT", body);
      showToast("Cập nhật hồ sơ thành công!");
      loadProfile();
    } catch (error) {}
  });
// =================================================================
// PART 4: USER'S ASSET MANAGEMENT (Vehicles & Batteries)
// =================================================================

let allMyVehicles = [];
let allMyBatteries = [];

/** Tải tất cả tài sản của người dùng. */
async function loadMyAssets() {
  loadMyVehicles();
  loadMyBatteries();
}

/** Tải danh sách xe của người dùng từ API và render. */
async function loadMyVehicles() {
  try {
    const vehicles = await apiRequest("/listing/api/my-assets/vehicles");
    allMyVehicles = vehicles && Array.isArray(vehicles) ? vehicles : [];
    renderMyVehicles();
  } catch (error) {
    console.error("Failed to load vehicles:", error);
    allMyVehicles = [];
    renderMyVehicles();
  }
}

/** Tải danh sách pin của người dùng từ API và render. */
async function loadMyBatteries() {
  try {
    const batteries = await apiRequest("/listing/api/my-assets/batteries");
    allMyBatteries = batteries && Array.isArray(batteries) ? batteries : [];
    renderMyBatteries();
  } catch (error) {
    console.error("Failed to load batteries:", error);
    allMyBatteries = [];
    renderMyBatteries();
  }
}

// Giả sử bạn có hàm renderMyVehicles như thế này
/*async*/ function renderMyVehicles(showAll = false) {
  const container = document.getElementById("my-vehicles-container");
  if (!container) return;

  const vehiclesToDisplay = showAll ? allMyVehicles : allMyVehicles.slice(0, 2);

  if (allMyVehicles.length === 0) {
    container.innerHTML =
      '<p class="text-center text-gray-500">Bạn chưa có xe nào.</p>';
    return;
  }

  const vehiclePromises = vehiclesToDisplay.map(
    /*async*/ (v) => {
      let statusBadge = "";
      let detailInfo = "";
      let primaryActions = "";
      let secondaryActions = `
            <button onclick='openModal("vehicle-modal", ${JSON.stringify(
              v
            )})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
            <button onclick="deleteVehicle(${
              v.vehicle_id
            })" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button>
        `;
      if (v.is_auctioned) {
        //statusBadge = `<span class="ml-2 bg-purple-200 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">Đang đấu giá</span>`;
        statusBadge = renderStatusAuction(v.auction_status_resource);
        detailInfo = `<button onclick="viewVehicleAuctionDetail('${v.vehicle_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
        primaryActions = `<button onclick="unauctionVehicle('${v.vehicle_id}')" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gỡ Đấu Giá</button>`;
        secondaryActions = "";
        // }else if (v.auction_status === "ended") {
        //     statusBadge = `<span class="ml-2 px-2 inline-flex text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Đấu giá kết thúc</span>`;
        //     detailInfo = `<button onclick="viewVehicleAuctionDetail('${v.vehicle_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
        //     primaryActions = '';
        //     secondaryActions = '';
        // } else if (v.auction_status === "rejected") {
        //     statusBadge = `<span class="ml-2 px-2 inline-flex text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Bị từ chối</span>`;
        //     primaryActions = `<button onclick="openAuctionModal('battery', ${v.vehicle_id})" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gửi lại đấu giá</button>`;
      } else if (v.is_listed) {
        statusBadge = renderStatusBadge(v.listing_status);
        detailInfo = `<button onclick="viewVehicleDetail('${v.vehicle_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem Chi Tiết</button>`;
        primaryActions = `<button onclick="unlistVehicle(${v.vehicle_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`;
      } else {
        detailInfo = `Dòng xe: ${
          v.model
        } | Số KM: ${v.mileage.toLocaleString()}`;
        primaryActions = `
                <button onclick="openListingModal('vehicle', ${v.vehicle_id})" class="bg-blue-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-blue-600">Đăng Bán</button>
                <button onclick="openAuctionModal('vehicle', ${v.vehicle_id})" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Đấu Giá</button>
            `;
      }

      return `
            <div class="border rounded-lg p-4 flex justify-between items-center bg-white">
                <div>
                    <p class="font-bold flex items-center">
                        Hãng xe: ${v.brand} (${v.year})
                        ${statusBadge}
                    </p>
                    <p class="text-sm text-gray-600">
                        ${detailInfo}
                    </p>
                </div>
                <div class="space-x-2 flex items-center">
                    ${primaryActions}
                    ${secondaryActions}
                </div>
            </div>
        `;
    }
  );

  // const htmlSnippets = await Promise.all(vehiclePromises);
  // let contentHTML = htmlSnippets.join("")
  let contentHTML = vehiclePromises.join("");
  if (allMyVehicles.length > 2) {
    contentHTML += `
            <div class="text-center mt-4">
                <button onclick="renderMyVehicles(${!showAll})" class="text-blue-600 hover:underline font-semibold">
                    ${
                      showAll
                        ? "Ẩn bớt"
                        : `Hiển thị toàn bộ (${allMyVehicles.length})`
                    }
                </button>
            </div>`;
  }

  container.innerHTML = contentHTML;
}

/**
 * Hiển thị danh sách pin của người dùng ra giao diện.
 * @param {boolean} showAll - True để hiển thị tất cả, false để chỉ hiển thị 2 pin đầu.
 */
/*async*/ function renderMyBatteries(showAll = false) {
  const container = document.getElementById("my-batteries-container");
  if (!container) return;

  if (!allMyBatteries || allMyBatteries.length === 0) {
    container.innerHTML = `<p class="text-center text-gray-500">Bạn chưa có pin nào.</p>`;
    return;
  }

  const batteriesToDisplay = showAll
    ? allMyBatteries
    : allMyBatteries.slice(0, 2);

  const batteryPromises = batteriesToDisplay.map(
    /*async*/ (b) => {
      let statusBadge = "";
      let detailInfo = "";
      let primaryActions = "";
      let secondaryActions = `
            <button onclick='openModal("battery-modal", ${JSON.stringify(
              b
            )})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
            <button onclick="deleteBattery(${
              b.battery_id
            })" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button>
        `;
      if (b.is_auctioned === true) {
        //statusBadge = await renderStatusBattery(b.battery_id);
        //statusBadge = `<span class="ml-2 bg-purple-200 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">Đang đấu giá</span>`;
        statusBadge = renderStatusAuction(b.auction_status_resource);
        detailInfo = `<button onclick="viewBatteryAuctionDetail('${b.battery_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
        primaryActions = `<button onclick="unauctionBattery('${b.battery_id}')" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gỡ Đấu Giá</button>`;

        secondaryActions = "";
      } else if (b.auction_status === "ended") {
        statusBadge = `<span class="ml-2 px-2 inline-flex text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Đấu giá kết thúc</span>`;
        detailInfo = `<button onclick="viewBatteryAuctionDetail('${b.battery_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
        primaryActions = "";
        secondaryActions = "";
      } else if (b.auction_status === "rejected") {
        statusBadge = `<span class="ml-2 px-2 inline-flex text-xs font-semibold rounded-full bg-gray-100 text-gray-800">Bị từ chối</span>`;
        primaryActions = `<button onclick="openAuctionModal('battery', ${b.battery_id})" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gửi lại đấu giá</button>`;
      } else if (b.is_listed) {
        statusBadge = renderStatusBadge(b.listing_status);
        detailInfo = `<button onclick="viewBatteryDetail('${b.battery_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem Chi Tiết</button>`;
        primaryActions = `<button onclick="unlistBattery(${b.battery_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`;
      } else {
        detailInfo = `Dung lượng: ${b.capacity_kwh} kWh | Tình trạng: ${b.health_percent}%`;
        primaryActions = `
                <button onclick="openListingModal('battery', ${b.battery_id})" class="bg-blue-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-blue-600">Đăng Bán</button>
                <button onclick="openAuctionModal('battery', ${b.battery_id})" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Đấu Giá</button>
            `;
      }
      return `
            <div class="border rounded-lg p-4 flex justify-between items-center bg-white">
                <div>
                    <p class="font-bold flex items-center">
                        Nhà sản xuất: ${b.manufacturer}
                        ${statusBadge}
                    </p>
                    <p class="text-sm text-gray-600">
                        ${detailInfo}
                    </p>
                </div>
                <div class="space-x-2 flex items-center">
                    ${primaryActions}
                    ${secondaryActions}
                </div>
            </div>
        `;
    }
  );
  // const htmlSnippets = await Promise.all(batteryPromises);
  // let contentHTML = htmlSnippets.join("");
  let contentHTML = batteryPromises.join("");
  if (allMyBatteries.length > 2) {
    contentHTML += `<div class="text-center mt-4">
            <button onclick="renderMyBatteries(${!showAll})" class="text-blue-600 hover:underline font-semibold">
                ${
                  showAll
                    ? "Ẩn bớt"
                    : `Hiển thị toàn bộ (${allMyBatteries.length})`
                }
            </button>
        </div>`;
  }
  container.innerHTML = contentHTML;
}

/** Xóa xe khỏi kho. */
async function deleteVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn xóa xe này khỏi kho?")) {
    try {
      await apiRequest(`/listing/api/my-assets/vehicles/${id}`, "DELETE");
      showToast("Xóa xe thành công.");
      loadMyVehicles();
    } catch (error) {}
  }
}

/** Xóa pin khỏi kho. */
async function deleteBattery(id) {
  if (confirm("Bạn có chắc chắn muốn xóa pin này khỏi kho?")) {
    try {
      await apiRequest(`/listing/api/my-assets/batteries/${id}`, "DELETE");
      showToast("Xóa pin thành công.");
      loadMyBatteries();
    } catch (error) {}
  }
}

// --- ASSET FORM EVENT LISTENERS ---

document
  .getElementById("vehicle-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("vehicle-id").value;
    const body = {
      brand: document.getElementById("vehicle-brand").value,
      model: document.getElementById("vehicle-model").value,
      year: parseInt(document.getElementById("vehicle-year").value),
      mileage: parseInt(document.getElementById("vehicle-mileage").value),
    };

    const method = id ? "PUT" : "POST";
    const endpoint = id
      ? `/listing/api/my-assets/vehicles/${id}`
      : "/listing/api/my-assets/vehicles";

    try {
      await apiRequest(endpoint, method, body);
      showToast(id ? "Cập nhật xe thành công." : "Thêm xe mới thành công.");
      closeModal("vehicle-modal");
      loadMyVehicles();
    } catch (error) {}
  });

document
  .getElementById("battery-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("battery-id").value;
    const body = {
      manufacturer: document.getElementById("battery-manufacturer").value,
      capacity_kwh: parseFloat(
        document.getElementById("battery-capacity").value
      ),
      health_percent: parseInt(document.getElementById("battery-health").value),
    };

    const method = id ? "PUT" : "POST";
    const endpoint = id
      ? `/listing/api/my-assets/batteries/${id}`
      : "/listing/api/my-assets/batteries";

    try {
      await apiRequest(endpoint, method, body);
      showToast(id ? "Cập nhật pin thành công." : "Thêm pin mới thành công.");
      closeModal("battery-modal");
      loadMyBatteries();
    } catch (error) {}
  });
// =================================================================
// PART 5: LISTINGS MANAGEMENT
// =================================================================

/** Mở modal để đăng bán một sản phẩm. */
function openListingModal(type, id) {
  openModal("listing-modal", { type, id });
}

/** Gỡ bán một chiếc xe. */
async function unlistVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ bán xe này?")) {
    try {
      await apiRequest(`/listing/api/my-assets/vehicles/${id}/list`, "DELETE");
      showToast("Gỡ bán xe thành công.");
      loadMyVehicles();
    } catch (error) {}
  }
}
/** Gỡ đấu giá một chiếc xe. */
async function unauctionVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ đấu giá xe này?")) {
    try {
      await apiRequest(`/auction/api/auctions/vehicles/${id}`, "DELETE");
      showToast("Gỡ đấu giá xe thành công.");
      loadMyVehicles();
    } catch (error) {}
  }
}
/** Gỡ đấu giá một viên pin. */
async function unauctionBattery(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ đấu giá pin này?")) {
    try {
      await apiRequest(`/auction/api/auctions/batteries/${id}`, "DELETE");
      showToast("Gỡ đấu giá pin thành công.");
      loadMyBatteries();
    } catch (error) {}
  }
}

/** Gỡ bán một viên pin. */
async function unlistBattery(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ bán pin này?")) {
    try {
      await apiRequest(`/listing/api/my-assets/batteries/${id}/list`, "DELETE");
      showToast("Gỡ bán pin thành công.");
      loadMyBatteries();
    } catch (error) {}
  }
}
 
async function loadPublicListings() {
    const container = document.getElementById("listings-container"); 
    container.innerHTML = `<div class="col-span-full text-center p-6 text-gray-500">Đang tải danh sách sản phẩm...</div>`;
    showLoading();   
    try { 
        const listings = await apiRequest("/listing/api/listings"); 
        renderListings(listings);  
    } catch (error) {
        console.error("Lỗi khi tải danh sách tin đăng:", error);  
        container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách tin đăng. Vui lòng thử lại.</p></div>`;
    } finally {
        hideLoading();  
    }
}

// --- LISTING FORM EVENT LISTENER ---
document.getElementById("filter-listing-type").addEventListener("change", function () {
  const type = this.value;
  document.getElementById("vehicle-filters").classList.add("hidden");
  document.getElementById("battery-filters").classList.add("hidden");
  if (type === "vehicle") document.getElementById("vehicle-filters").classList.remove("hidden");
  if (type === "battery") document.getElementById("battery-filters").classList.remove("hidden");
});

// Gọi API lọc listings
async function applyListingFilter() {
  const params = new URLSearchParams();

  const listing_type = document.getElementById("filter-listing-type").value;
  const title = document.getElementById("filter-title").value;
  const min_price = document.getElementById("filter-min-price").value;
  const max_price = document.getElementById("filter-max-price").value;

  if (listing_type) params.append("listing_type", listing_type);
  if (title) params.append("title", title);
  if (min_price) params.append("min_price", min_price);
  if (max_price) params.append("max_price", max_price);

  // Nếu là vehicle
  if (listing_type === "vehicle") {
    const brand = document.getElementById("filter-brand").value;
    const model = document.getElementById("filter-model").value;
    const year = document.getElementById("filter-year").value;
    if (brand) params.append("brand", brand);
    if (model) params.append("model", model);
    if (year) params.append("year", year);
  }

  // Nếu là battery
  if (listing_type === "battery") {
    const manufacturer = document.getElementById("filter-manufacturer").value;
    const capacity_min = document.getElementById("filter-capacity-min").value;
    const capacity_max = document.getElementById("filter-capacity-max").value;
    if (manufacturer) params.append("manufacturer", manufacturer);
    if (capacity_min) params.append("capacity_min", capacity_min);
    if (capacity_max) params.append("capacity_max", capacity_max);
  }

  const container = document.getElementById("listings-container");
  container.innerHTML = `<div class="col-span-full text-center p-6 text-gray-500">Đang lọc dữ liệu...</div>`;

  try {
    const listings = await apiRequest(`/listing/api/listings/filter?${params.toString()}`);
    if (listings && listings.length > 0) {
      renderListings(listings);
    } else {
      container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-gray-600">Không có kết quả phù hợp.</p></div>`;
    }
  } catch (error) {
    console.error("❌ Lỗi khi lọc:", error);
    container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Lỗi khi lọc dữ liệu.</p></div>`;
  }
}
// Function to render the list of listings
function renderListings(listings) {
    const container = document.getElementById("listings-container");
    if (!container) return;  
    container.innerHTML = '';  
    if (!Array.isArray(listings) || listings.length === 0) {
        container.innerHTML = `
        <div class="col-span-full text-center bg-white p-12 rounded-lg shadow">
             <h3 class="mt-2 text-sm font-medium text-gray-900">Không có tin đăng nào</h3>
             <p class="mt-1 text-sm text-gray-500">Hiện tại không có sản phẩm nào đang được bán hoặc phù hợp với bộ lọc.</p>
        </div>`;
        return;
    } 
    container.innerHTML = listings.map((item) => {
        let detailsHtml = ""; 
        if (item.listing_type === "vehicle" && item.vehicle_details) {
            const v = item.vehicle_details;
            detailsHtml = `
              <p class="text-gray-600">Hãng xe: ${v.brand ?? '?'} | Dòng xe: ${v.model ?? 'N/A'} | Năm: ${v.year ?? '?'}</p>
              <p class="text-sm text-gray-500">Số KM: ${(v.mileage ?? 0).toLocaleString()}</p>
            `;
        } else if (item.listing_type === "battery" && item.battery_details) {
            const b = item.battery_details;
            detailsHtml = `
              <p class="text-gray-600">Nhà SX: ${b.manufacturer ?? 'N/A'}</p>
              <p class="text-sm text-gray-500">${b.capacity_kwh ?? '?'}kWh | ${b.health_percent ?? '?'}%</p>
            `;
        }

        const imageUrl = item.images && item.images.length > 0
                         ? apiBaseUrl + item.images[0]
                         : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+";
        const priceFormatted = Number(item.price || 0).toLocaleString();  
        return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden flex flex-col transition-transform transform hover:-translate-y-1">
            <div class="relative w-full h-48 bg-gray-200">
                <img src="${imageUrl}" alt="${item.title ?? 'Sản phẩm'}" class="w-full h-full object-cover">
            </div>
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold text-lg mb-2 truncate" title="${item.title ?? ''}">${item.title ?? 'Chưa có tiêu đề'}</h3>
                <div class="flex-grow mb-4">${detailsHtml}</div>
                <div class="mt-auto flex justify-between items-center">
                    <p class="text-indigo-600 font-bold text-xl">${priceFormatted} VNĐ</p>
                    <div class="flex items-center space-x-2">
                        <button onclick="addToWatchlist(${item.listing_id})" title="Thêm vào danh sách theo dõi" class="text-gray-400 hover:text-teal-500 p-2 rounded-full hover:bg-gray-100 transition duration-300">
                            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                            </svg>
                        </button>
                        <button onclick="viewDetail('${item.listing_id}', '${item.seller_id}', '${item.price}')" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                    </div>
                </div>
            </div>
        </div>
        `;
    }).join(""); 
}
document
  .getElementById("listing-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("listing-item-id").value;
    const type = document.getElementById("listing-item-type").value;
    const body = {
      title: document.getElementById("listing-title").value,
      price: parseFloat(document.getElementById("listing-price").value),
      description: document.getElementById("listing-description").value,
    };

    const assetType = type === "battery" ? "batteries" : "vehicles";
    const endpoint = `/listing/api/my-assets/${assetType}/${id}/list`;

    try {
      await apiRequest(endpoint, "POST", body);
      showToast("Đăng bán thành công!");
      closeModal("listing-modal");
      if (type === "vehicle") loadMyVehicles();
      if (type === "battery") loadMyBatteries();
    } catch (error) {
      // Lỗi đã được showToast xử lý trong apiRequest
    }
  });
// =================================================================
// PART 6: AUCTIONS MANAGEMENT
// =================================================================

/** Mở modal để tạo một phiên đấu giá. */
function openAuctionModal(type, id) {
  openModal("auction-modal", { type, id });
}
 
async function loadPublicAuctions() {
    const container = document.getElementById("auctions-container"); 
    container.innerHTML = `<div class="col-span-full text-center p-6 text-gray-500">Đang tải danh sách đấu giá...</div>`;
    showLoading();  

    try { 
        const auctions = await apiRequest("/auction/api/");  
        renderAuctions(auctions); 

    } catch (error) {
        console.error("Lỗi khi tải danh sách đấu giá:", error); 
        container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách đấu giá.</p></div>`;
    } finally {
        hideLoading();  
    }
}
async function applyAuctionFilter() { 
    const params = new URLSearchParams(); 
    const auction_type = document.getElementById("filter-auction-type").value;
    if (auction_type) {
        params.append("type", auction_type);  
    } 
    const container = document.getElementById("auctions-container");
    container.innerHTML = `<div class="col-span-full text-center p-6 text-gray-500">Đang lọc phiên đấu giá...</div>`; 
    try { 
        const auctions = await apiRequest(`/auction/api/filter?${params.toString()}`, 'GET', null, 'auction');  
        if (auctions && Array.isArray(auctions) && auctions.length > 0) {
            renderAuctions(auctions);  
        } else {
            container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-gray-600">Không có phiên đấu giá nào phù hợp.</p></div>`;
        }
    } catch (error) { 
        console.error("❌ Lỗi khi lọc đấu giá:", error);
        container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Lỗi khi lọc dữ liệu đấu giá.</p></div>`;
    }
} 
function renderAuctions(auctions) {
    const container = document.getElementById('auctions-container');
    if (!container) return; 
    container.innerHTML = '';  
    if (!Array.isArray(auctions) || auctions.length === 0) {
        container.innerHTML = `
        <div class="col-span-full text-center bg-white p-12 rounded-lg shadow">
             <h3 class="mt-2 text-sm font-medium text-gray-900">Không có phiên đấu giá nào</h3>
             <p class="mt-1 text-sm text-gray-500">Hiện tại không có sản phẩm nào đang được đấu giá hoặc phù hợp với bộ lọc.</p>
        </div>`;
        return;
    } 
    container.innerHTML = auctions.map(item => { 
        let detailsHtml = ""; 
        if (item.auction_type === "vehicle" && item.vehicle_details) {
            const v = item.vehicle_details; 
            detailsHtml = `<p class="text-sm text-purple-700 bg-purple-100 px-2 py-1 rounded inline-block">Xe: ${v?.brand ?? '?'} ${v?.model ?? 'N/A'}</p>`;
        } else if (item.auction_type === "battery" && item.battery_details) {
            const b = item.battery_details; 
            detailsHtml = `<p class="text-sm text-green-700 bg-green-100 px-2 py-1 rounded inline-block">Pin: ${b?.manufacturer ?? (b?.name ?? 'N/A')}</p>`;
        } else {
             detailsHtml = `<p class="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded inline-block">Loại: ${item.auction_type ?? 'N/A'}</p>`;
        }

        const startTime = new Date(item.start_time).toLocaleString("vi-VN");
        const endTime = new Date(item.end_time).toLocaleString("vi-VN");
        const currentBid = Number(item.current_bid || 0).toLocaleString(); 
        return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden flex flex-col transition-transform transform hover:-translate-y-1">
            <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold text-lg mb-2 truncate">Phiên đấu giá #${item.auction_id}</h3>
                 <span class="mb-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    item.auction_status === 'prepare' ? 'bg-blue-100 text-blue-800' :
                    item.auction_status === 'started' ? 'bg-red-100 text-red-800' :
                    item.auction_status === 'ended' ? 'bg-gray-100 text-gray-800' :
                    item.auction_status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-gray-100 text-gray-800'  
                 }">
                    ${item.auction_status}
                </span>
                <div class="my-2">${detailsHtml}</div>
                <div class="flex-grow mb-4 text-sm text-gray-500">
                    <p>Bắt đầu: ${startTime}</p>
                    <p>Kết thúc: ${endTime}</p>
                </div>
                <div class="mt-auto flex justify-between items-center">
                    <div>
                        <p class="text-sm text-gray-500">Giá hiện tại:</p>
                        <p class="text-indigo-600 font-bold text-xl">${currentBid} VNĐ</p>
                    </div>
                    <button onclick="viewAuctionDetail(${item.auction_id})" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                </div>
            </div>
        </div>
        `;
    }).join(""); 
}

// --- AUCTION FORM EVENT LISTENER ---

document
  .getElementById("auction-form")
  .addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("auction-item-id").value;
    const type = document.getElementById("auction-item-type").value;
    const startTime = document.getElementById("auction-start-time").value;
    const startBid = parseFloat(
      document.getElementById("auction-start-bid").value
    );

    if (!startTime || !startBid || startBid <= 0) {
      showToast("Vui lòng nhập ngày bắt đầu và giá khởi điểm hợp lệ.", true);
      return;
    }

    const body = {
      auction_type: type,
      start_time: startTime, 
      current_bid: startBid,
    };

    if (type === "vehicle") {
      body.vehicle_id = parseInt(id);
    } else if (type === "battery") {
      body.battery_id = parseInt(id);
    }

    try {
      await apiRequest("/auction/api/", "POST", body);
      showToast("Tạo đấu giá thành công! Đang chờ duyệt.");
      closeModal("auction-modal");
      if (type === "vehicle") loadMyVehicles();
      if (type === "battery") loadMyBatteries();
    } catch (error) {
      console.error("Failed to create auction:", error);
    }
  });

// =================================================================
// PART 7: WATCHLIST MANAGEMENT
// =================================================================

/** Tải và hiển thị danh sách theo dõi của người dùng. */
async function loadMyWatchlist() {
  showLoading();
  try {
    const listings = await apiRequest("/listing/api/watch-list");
    const container = document.getElementById("watchlist-container");

    if (!container) return;

    if (!listings || listings.length === 0) {
      container.innerHTML = `
            <div class="col-span-full text-center bg-white p-12 rounded-lg shadow">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">Danh sách trống</h3>
                <p class="mt-1 text-sm text-gray-500">Bạn chưa có dữ liệu nào trong danh sách theo dõi.</p>
            </div>`;
      return;
    }

    container.innerHTML = listings
      .map((listing) => {
        let detailsHtml = "";
        if (listing.listing_type === "vehicle" && listing.vehicle_details) {
          const v = listing.vehicle_details;
          detailsHtml = `
                    <p class="text-gray-600">Hãng xe: ${v.brand} | Dòng xe: ${
            v.model
          } | Năm sản xuất: ${v.year}</p>
                    <p class="text-sm text-gray-500">Số KM: ${v.mileage.toLocaleString()}</p>`;
        } else if (
          listing.listing_type === "battery" &&
          listing.battery_details
        ) {
          const b = listing.battery_details;
          detailsHtml = `
                    <p class="text-gray-600">Nhà sản xuất: ${b.manufacturer}</p>
                    <p class="text-sm text-gray-500">${b.capacity_kwh}kWh | Tình trạng: ${b.health_percent}%</p>`;
        }

        const imageUrl =
          listing.images && listing.images.length > 0
            ? apiBaseUrl + listing.images[0]
            : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+";
        const formattedPrice =
          parseFloat(listing.price).toLocaleString("vi-VN") + " VNĐ";

        return `
            <div class="bg-white rounded-lg shadow-md overflow-hidden flex flex-col transition-transform transform hover:-translate-y-1">
                <div class="relative w-full h-48 bg-gray-200">
                    <img src="${imageUrl}" alt="${listing.title}" class="w-full h-full object-cover">
                </div>
                <div class="p-4 flex flex-col flex-grow">
                    <h3 class="font-bold text-lg mb-2 truncate" title="${listing.title}">${listing.title}</h3>
                    <div class="flex-grow mb-4">${detailsHtml}</div>
                    <div class="mt-auto flex justify-between items-center">
                        <p class="text-indigo-600 font-bold text-xl">${formattedPrice}</p>
                        <div class="flex items-center space-x-2">
                            <button onclick="removeFromWatchlist(this, ${listing.listing_id})" title="Bỏ theo dõi" class="text-gray-400 hover:text-red-500 p-2 rounded-full hover:bg-gray-100 transition duration-300">
                                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                            <button onclick="viewDetail('${listing.listing_id}', '${listing.seller_id}', '${listing.price}')" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                        </div>
                    </div>
                </div>
            </div>`;
      })
      .join("");
  } catch (error) {
    console.error("Failed to load watchlist:", error);
    const container = document.getElementById("watchlist-container");
    if (container) {
      container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách theo dõi. Vui lòng thử lại.</p></div>`;
    }
  } finally {
    hideLoading();
  }
}


 /* Thêm một sản phẩm vào danh sách theo dõi.*/

async function addToWatchlist(listingId) {
  if (!isLoggedIn()) {
    alert("Bạn phải đăng nhập để sử dụng chức năng này.");
    navigateTo("login");
    return;
  }
  showLoading();
  try {
    const response = await apiRequest(`/listing/api/watch-list`, "POST", {
      listing_id: listingId,
    });
    showToast(response.message || "Đã thêm vào danh sách theo dõi thành công!");
  } catch (error) {
  } finally {
    hideLoading();
  }
}
 /* xóa một sản phẩm ra danh sách theo dõi.*/
async function removeFromWatchlist(buttonElement, listingId) {
  if (!confirm("Bạn có chắc muốn bỏ theo dõi tin đăng này?")) {
    return;
  }
  showLoading();
  try {
    await apiRequest(
      `/listing/api/watch-list/by-listing/${listingId}`,
      "DELETE"
    );
    showToast("Đã bỏ theo dõi thành công.");
    const card = buttonElement.closest(".bg-white.rounded-lg.shadow-md");
    if (card) {
      card.style.transition = "opacity 0.5s ease";
      card.style.opacity = "0";
      setTimeout(() => {
        card.remove();
        // Kiểm tra xem container có rỗng không
        const container = document.getElementById("watchlist-container");
        if (container && container.children.length === 0) {
          loadMyWatchlist(); // Tải lại để hiển thị thông báo rỗng
        }
      }, 500);
    } else {
      loadMyWatchlist();
    }
  } catch (error) {
    console.error("Failed to remove from watchlist:", error);
  } finally {
    hideLoading();
  }
}
// =================================================================
// PART 8: ITEM DETAILS & IMAGE UPLOAD
// =================================================================

/** Hiển thị chi tiết một tin đăng bán công khai. */
async function viewDetail(listingId, sellerId, finalPrice) {
  const modalContent = document.getElementById("detail-modal-content");
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  document.getElementById("add-image-btn")?.remove();
  const buttonDiv = document.getElementById("button_div");
  const existingBuyButton = document.getElementById("buy-listing");
  if (sellerId && finalPrice) {
    let btn = existingBuyButton;
    if (!btn) {
      btn = document.createElement("button");
      btn.id = "buy-listing";
      btn.textContent = "Mua";
      btn.className =
        "bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600";
      buttonDiv.prepend(btn);
    }
    btn.onclick = () => buyListing(listingId, sellerId, finalPrice);
  } else {
    existingBuyButton?.remove();
  }
  openModal("detail-modal");

  try {
    const listing = await apiRequest(`/listing/api/listings/${listingId}`);
    if (listing) {
      renderListingDetail(listing);
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}

/** Hiển thị chi tiết một chiếc xe từ kho cá nhân. */
async function viewVehicleDetail(vehicle_id) {
  const modalContent = document.getElementById("detail-modal-content");
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  document.getElementById("buy-listing")?.remove();
  const buttonDiv = document.getElementById("button_div");
  let btn = document.getElementById("add-image-btn");
  if (!btn) {
    btn = document.createElement("button");
    btn.id = "add-image-btn";
    btn.textContent = "Cập nhật ảnh";
    btn.className =
      "bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600";
    buttonDiv.prepend(btn);
  }
  btn.onclick = () => uploadImage(vehicle_id, "vehicle");
  openModal("detail-modal");
  try {
    const listing = await apiRequest(
      `/listing/api/listings/vehicle/${vehicle_id}`
    );
    if (listing) {
      renderListingDetail(listing);
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}

/** Hiển thị chi tiết một viên pin từ kho cá nhân. */
async function viewBatteryDetail(battery_id) {
  const modalContent = document.getElementById("detail-modal-content");
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  document.getElementById("buy-listing")?.remove();
  const buttonDiv = document.getElementById("button_div");
  let btn = document.getElementById("add-image-btn");
  if (!btn) {
    btn = document.createElement("button");
    btn.id = "add-image-btn";
    btn.textContent = "Cập nhật ảnh";
    btn.className =
      "bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600";
    buttonDiv.prepend(btn);
  }
  btn.onclick = () => uploadImage(battery_id, "battery");
  openModal("detail-modal");
  try {
    const listing = await apiRequest(
      `/listing/api/listings/battery/${battery_id}`
    );
    if (listing) {
      renderListingDetail(listing);
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}

/** Render nội dung HTML cho modal chi tiết tin đăng. */
function renderListingDetail(item) {
  const modalContent = document.getElementById("detail-modal-content");
  let productDetailsHtml = "";
  if (item.listing_type === "vehicle" && item.vehicle_details) {
    const v = item.vehicle_details;
    productDetailsHtml = `
            <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                <p><strong>Hãng xe:</strong> ${v.brand}</p>
                <p><strong>Dòng xe:</strong> ${v.model}</p>
                <p><strong>Năm sản xuất:</strong> ${v.year}</p>
                <p><strong>Số KM đã đi:</strong> ${v.mileage.toLocaleString()}</p>
            </div>`;
  } else if (item.listing_type === "battery" && item.battery_details) {
    const b = item.battery_details;
    productDetailsHtml = `
            <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                <p><strong>Nhà sản xuất:</strong> ${b.manufacturer}</p>
                <p><strong>Dung lượng:</strong> ${b.capacity_kwh} kWh</p>
                <p><strong>Tình trạng:</strong> ${b.health_percent}%</p>
            </div>`;
  }

  modalContent.innerHTML = `
        <h3 class="text-2xl font-bold mb-2">Tiêu đề: ${item.title}</h3>
        <p class="text-2xl font-bold text-indigo-600 mb-4">Giá: ${Number(
          item.price
        ).toLocaleString()} VNĐ</p>
        <div class="w-full h-64 md:h-80 bg-gray-200 rounded-lg mb-4">
             <img src="${
               item.images[0]
                 ? apiBaseUrl + item.images[0]
                 : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+"
             }"
                  alt="Hình ảnh sản phẩm" class="w-full h-full object-contain">
        </div>
        <h4 class="text-lg font-semibold">Mô tả</h4>
        <p class="text-gray-700 mt-1 whitespace-pre-wrap">${
          item.description || "Không có mô tả."
        }</p>
        ${productDetailsHtml}
    `;
}
/** Hiển thị chi tiết đấu giá một pin từ kho cá nhân. */
async function viewBatteryAuctionDetail(battery_id) {
  const modalContent = document.getElementById("detail-modal-content");
  document.getElementById("add-image-btn")?.remove();
  document.getElementById("buy-listing")?.remove();
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  openModal("detail-modal");

  try {
    const item = await apiRequest(`/auction/api/battery/${battery_id}`);
    if (item) {
      let productDetailsHtml = "";
      productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Nhà sản xuất:</strong> ${
                      item.battery_details.manufacturer || "N/A"
                    }</p>
                    <p><strong>Dung lượng:</strong> ${
                      item.battery_details.capacity_kwh
                        ? item.battery_details.capacity_kwh + " kWh"
                        : "N/A"
                    }</p>
                    <p><strong>Tình trạng:</strong> ${
                      item.battery_details.health_percent
                        ? item.battery_details.health_percent + "%"
                        : "N/A"
                    }</p>
                    </div>`;
      modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${
                  item.auction_id
                }</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(
                  item.current_bid
                ).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(
                  item.start_time
                ).toLocaleString("vi-VN")}</p>
                <p><strong>Kết thúc:</strong> ${new Date(
                  item.end_time
                ).toLocaleString("vi-VN")}</p>
                ${productDetailsHtml}
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Thông tin đấu giá</h4>
                <p>Người bán: ${
                  item.seller_username
                    ? `${item.seller_username} (ID: ${item.bidder_id})`
                    : `ID: ${item.bidder_id}`
                }</p> 
                <p>Người thắng hiện tại: ${
                  item.winner_username
                    ? `${item.winner_username} (ID: ${item.winning_bidder_id})`
                    : item.winning_bidder_id
                    ? `ID: ${item.winning_bidder_id}`
                    : "N/A"
                }</p>
                ${
                  item.auction_status === "started"
                    ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${
                      Number(item.current_bid) + 1
                    }"
                           placeholder="Phải lớn hơn ${Number(
                             item.current_bid
                           ).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                `
                    : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`
                }
            `;
      const auctionId = item.auction_id;

      const bidForm = document.getElementById("bid-form");
      if (bidForm) {
        bidForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const bidAmount = document.getElementById("bid-amount").value;
          try {
            await apiRequest(`/auction/api/${auctionId}/bid`, "POST", {
              bid_amount: parseFloat(bidAmount),
            });
            showToast("Đặt giá thành công!");
            closeModal("detail-modal");
            loadPublicAuctions();
          } catch (error) {}
        });
      }
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}
/** Hiển thị chi tiết đấu giá một chiếc xe từ kho cá nhân. */
async function viewVehicleAuctionDetail(vehicle_id) {
  const modalContent = document.getElementById("detail-modal-content");
  document.getElementById("add-image-btn")?.remove();
  document.getElementById("buy-listing")?.remove();
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  openModal("detail-modal");

  try {
    const item = await apiRequest(`/auction/api/vehicle/${vehicle_id}`);
    if (item) {
      let productDetailsHtml = "";
      productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Hãng xe:</strong> ${
                      item.vehicle_details.brand || "N/A"
                    }</p>
                    <p><strong>Dòng xe:</strong> ${
                      item.vehicle_details.model || "N/A"
                    }</p>
                    <p><strong>Năm sản xuất:</strong> ${
                      item.vehicle_details.year || "N/A"
                    }</p>
                    <p><strong>Số KM đã đi:</strong> ${
                      item.vehicle_details.mileage
                        ? item.vehicle_details.mileage.toLocaleString()
                        : "N/A"
                    }</p>
                    </div>`;
      modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${
                  item.auction_id
                }</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(
                  item.current_bid
                ).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(
                  item.start_time
                ).toLocaleString("vi-VN")}</p>
                <p><strong>Kết thúc:</strong> ${new Date(
                  item.end_time
                ).toLocaleString("vi-VN")}</p>
                ${productDetailsHtml}
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Người bán</h4>
                <p>Người bán: ${
                  item.seller_username
                    ? `${item.seller_username} (ID: ${item.bidder_id})`
                    : `ID: ${item.bidder_id}`
                }</p> 
                <p>Người thắng hiện tại: ${
                  item.winner_username
                    ? `${item.winner_username} (ID: ${item.winning_bidder_id})`
                    : item.winning_bidder_id
                    ? `ID: ${item.winning_bidder_id}`
                    : "N/A"
                }</p>
                ${
                  item.auction_status === "started"
                    ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${
                      Number(item.current_bid) + 1
                    }"
                           placeholder="Phải lớn hơn ${Number(
                             item.current_bid
                           ).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                `
                    : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`
                }
            `;
      const auctionId = item.auction_id;

      const bidForm = document.getElementById("bid-form");
      if (bidForm) {
        bidForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const bidAmount = document.getElementById("bid-amount").value;
          try {
            await apiRequest(`/auction/api/${auctionId}/bid`, "POST", {
              bid_amount: parseFloat(bidAmount),
            });
            showToast("Đặt giá thành công!");
            closeModal("detail-modal");
            loadPublicAuctions();
          } catch (error) {}
        });
      }
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}
/** Hiển thị chi tiết một phiên đấu giá và form đặt giá. */
async function viewAuctionDetail(auctionId) {
  const modalContent = document.getElementById("detail-modal-content");
  document.getElementById("add-image-btn")?.remove();
  document.getElementById("buy-listing")?.remove();
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  openModal("detail-modal");

  try {
    const item = await apiRequest(`/auction/api/${auctionId}`);
    if (item) {
      let productDetailsHtml = "";
      if (item.auction_type === "vehicle" && item.vehicle_details) {
        productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Hãng xe:</strong> ${
                      item.vehicle_details.brand || "N/A"
                    }</p>
                    <p><strong>Dòng xe:</strong> ${
                      item.vehicle_details.model || "N/A"
                    }</p>
                    <p><strong>Năm sản xuất:</strong> ${
                      item.vehicle_details.year || "N/A"
                    }</p>
                    <p><strong>Số KM đã đi:</strong> ${
                      item.vehicle_details.mileage
                        ? item.vehicle_details.mileage.toLocaleString()
                        : "N/A"
                    }</p>
                    </div>`;
      } else if (item.auction_type === "battery" && item.battery_details) {
        productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Nhà sản xuất:</strong> ${
                      item.battery_details.manufacturer || "N/A"
                    }</p>
                    <p><strong>Dung lượng:</strong> ${
                      item.battery_details.capacity_kwh
                        ? item.battery_details.capacity_kwh + " kWh"
                        : "N/A"
                    }</p>
                    <p><strong>Tình trạng:</strong> ${
                      item.battery_details.health_percent
                        ? item.battery_details.health_percent + "%"
                        : "N/A"
                    }</p>
                    </div>`;
      }

      modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${
                  item.auction_id
                }</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(
                  item.current_bid
                ).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(
                  item.start_time
                ).toLocaleString("vi-VN")}</p>
                <p><strong>Kết thúc:</strong> ${new Date(
                  item.end_time
                ).toLocaleString("vi-VN")}</p>
                ${productDetailsHtml}
                
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Người bán</h4>
                <p>Người bán: ${
                  item.seller_username
                    ? `${item.seller_username} (ID: ${item.bidder_id})`
                    : `ID: ${item.bidder_id}`
                }</p> 
                <p>Người thắng hiện tại: ${
                  item.winner_username
                    ? `${item.winner_username} (ID: ${item.winning_bidder_id})`
                    : item.winning_bidder_id
                    ? `ID: ${item.winning_bidder_id}`
                    : "N/A"
                }</p>
                ${
                  item.auction_status === "started"
                    ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${
                      Number(item.current_bid) + 1
                    }"
                           placeholder="Phải lớn hơn ${Number(
                             item.current_bid
                           ).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                `
                    : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`
                }
            `;

      const bidForm = document.getElementById("bid-form");
      if (bidForm) {
        bidForm.addEventListener("submit", async (e) => {
          e.preventDefault();
          const bidAmount = document.getElementById("bid-amount").value;
          try {
            await apiRequest(`/auction/api/${auctionId}/bid`, "POST", {
              bid_amount: parseFloat(bidAmount),
            });
            showToast("Đặt giá thành công!");
            closeModal("detail-modal");
            loadPublicAuctions();
          } catch (error) {}
        });
      }
    } else {
      modalContent.innerHTML =
        '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
    }
  } catch (error) {
    modalContent.innerHTML =
      '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}
/** Render nội dung HTML cho modal chi tiết giao dịch. */
function renderTransactions(containerId, transactions, emptyMessage) {
  const container = document.getElementById(containerId);
  if (!container) return;
  if (!Array.isArray(transactions) || transactions.length === 0) {
    container.innerHTML = `
            <div class="col-span-full text-center bg-white p-12 rounded-lg shadow">
                <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H7a3 3 0 00-3 3v8a3 3 0 003 3z" />
                </svg>
                <h3 class="mt-2 text-sm font-medium text-gray-900">Danh sách trống</h3>
                <p class="mt-1 text-sm text-gray-500">${emptyMessage}</p>
            </div>`;
    if (transactions && !Array.isArray(transactions)) {
      console.warn(
        "renderTransactions: Dữ liệu nhận được không phải là một mảng:",
        transactions
      );
    }
    return;
  }
  container.innerHTML = transactions
    .map((t) => {
      const isBuyer = getUserIdFromToken() == t.buyer_id;
      const isSeller = getUserIdFromToken() == t.seller_id;
      const formattedDate = new Date(t.created_at).toLocaleDateString("vi-VN");
      const imageUrl = t.listing_image
        ? apiBaseUrl + t.listing_image
        : "https://placehold.co/400x400/e2e8f0/e2e8f0?text=Giao+dịch";

      return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden flex items-center">
            <div class="w-32 h-32 flex-shrink-0 bg-gray-200">
                <img src="${imageUrl}" alt="${
        t.listing_id
      }" class="w-full h-full object-cover">
            </div>
            <div class="p-4 flex-grow">
            <p class="text-sm text-gray-500 mt-2">Mã giao dịch: #${t.transaction_id}</p>
                <p class="text-indigo-600 font-bold text-xl">ID người bán(bạn): ${
                  t.seller_id
                } || ID người mua: ${t.buyer_id}</p>
                <p class="text-sm text-gray-500 mt-2">Ngày giao dịch: ${formattedDate}</p>
                <button onclick="viewDetail(${
                  t.listing_id
                })" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">
                    Xem chi tiết sản phẩm
                </button>
                </div>           
            <div class="p-4">
                <button 
                    onclick='viewContract(${t.transaction_id})'
                    class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">
                    Xem hợp đồng
                </button>
                ${
                  isBuyer
                    ? `
                <button 
                    onclick="openPaymentModal(JSON.parse(decodeURIComponent('${encodeURIComponent(JSON.stringify(t))}')))" 
                    class="bg-green-600 text-white text-sm font-bold py-2 px-4 rounded hover:bg-green-700">
                    Than toán
                </button>
            `
                    : ""
                }
                ${
                  isSeller
                    ? `
                <button 
                    onclick="openPaymentStatusModal(${t.transaction_id})" 
                    class="bg-green-600 text-white text-sm font-bold py-2 px-4 rounded hover:bg-green-700">
                    Trạng thái
                </button>
            `
                    : ""
                }
                <button onclick="cancelTransaction(${
                  t.transaction_id
                })" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">
                    Hủy giao dịch
                </button>
            </div>
        </div>
        `;
    })
    .join("");
}
/** Hiển thị hợp đồng giao dịch. */
async function viewContract(transactionId) {
  showLoading();
  try {
    const response = await apiRequest(
      `/transaction/api/transactions/${transactionId}/contract`,
      "GET",
      null,
      "transaction"
    );

    if (response && response.transaction && response.contract) {
      openContractModal(response.transaction, response.contract);
    } else {
      throw new Error(response.error || "Không thể tải hợp đồng.");
    }
  } catch (error) {
    console.error("Lỗi khi xem hợp đồng:", error);
    showToast(`Lỗi: ${error.message}`, "error");
  } finally {
    hideLoading();
  }
}
/** Hủy giao dịch. */
async function cancelTransaction(id) {
  if (confirm("Bạn có chắc chắn hủy giao dịch này?")) {
    try {
      await apiRequest(`/transaction/api/transactions/${id}`, "DELETE");
      showToast("Hủy giao dịch thành công.");
      loadMyTransactions();
    } catch (error) {}
  }
}
/** Hiển thị toàn bộ giao dịch. */
async function loadMyTransactions() {
  showLoading();
  try {
    const salesTransactions = await apiRequest(
      "/transaction/api/transactions-seller"
    );
    renderTransactions(
      "sales-transactions-container",
      salesTransactions,
      "Bạn chưa có giao dịch bán nào."
    );
  } catch (error) {
    console.error("Failed to load sales transactions:", error);
    const container = document.getElementById("sales-transactions-container");
    if (container)
      container.innerHTML = `<div class="bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Lỗi tải giao dịch bán.</p></div>`;
  }
  try {
    const purchaseTransactions = await apiRequest(
      "/transaction/api/transactions-buyer"
    );
    renderTransactions(
      "purchase-transactions-container",
      purchaseTransactions,
      "Bạn chưa có giao dịch mua nào."
    );
  } catch (error) {
    console.error("Failed to load purchase transactions:", error);
    const container = document.getElementById(
      "purchase-transactions-container"
    );
    if (container)
      container.innerHTML = `<div class="bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Lỗi tải giao dịch mua.</p></div>`;
  }

  hideLoading();
}
/** Mua xe/pin. */
async function buyListing(listingId, sellerId, finalPrice) {
  const token = localStorage.getItem("jwt_token");

  if (!token) {
    showToast("Bạn cần đăng nhập để thực hiện giao dịch.", "error");
    return;
  }
  const buyButton = document.getElementById(`buy-listing`);

  let originalButtonText = "Mua Ngay";
  if (buyButton) {
    originalButtonText = buyButton.textContent;
    buyButton.disabled = true;
    buyButton.textContent = "Đang tạo...";
  }
  showLoading();

  try {
    const payload = {
      listing_id: listingId,
      seller_id: sellerId,
      final_price: finalPrice,
    };

    const response = await apiRequest(
      `/transaction/api/transactions`,
      "POST",
      payload,
      "transaction"
    );
    if (response && response.transaction && response.contract) {
      showToast(response.message || "Đã tạo giao dịch. Vui lòng ký hợp đồng.");
      closeModal("detail-modal");
      openContractModal(response.transaction, response.contract);
    } else {
      throw new Error(response.error || "Phản hồi từ máy chủ không hợp lệ.");
    }
  } catch (error) {
    console.error("Lỗi khi tạo giao dịch:", error);
    const errorMessage = error.message || "Đã xảy ra lỗi. Vui lòng thử lại.";
    showToast(`Tạo giao dịch thất bại: ${errorMessage}`, "error");
  } finally {
    hideLoading();
    if (buyButton) {
      buyButton.disabled = false;
      buyButton.textContent = originalButtonText;
    }
  }
}
/** Mở hợp đồng giao dịch. */
function openContractModal(transaction, contract) {
  document.getElementById("contract-transaction-id").value =
    transaction.transaction_id;
  document.getElementById("contract-terms-content").textContent =
    contract.term || "Không có điều khoản hợp đồng.";
  const currentUserId = getUserIdFromToken();
  const buyerStatus = document.getElementById("buyer-signature-status");
  const sellerStatus = document.getElementById("seller-signature-status");
  let buyerText = `Người mua (ID: ${transaction.buyer_id}): ${
    contract.signed_by_buyer ? "Đã ký" : "Chưa ký"
  }`;
  let sellerText = `Người bán (ID: ${transaction.seller_id}): ${
    contract.signed_by_seller ? "Đã ký" : "Chưa ký"
  }`;
  if (currentUserId == transaction.buyer_id) buyerText += " (Bạn)";
  if (currentUserId == transaction.seller_id) sellerText += " (Bạn)";
  buyerStatus.textContent = buyerText;
  sellerStatus.textContent = sellerText;
  buyerStatus.className = contract.signed_by_buyer
    ? "text-sm font-medium text-green-600"
    : "text-sm font-medium text-red-600";
  sellerStatus.className = contract.signed_by_seller
    ? "text-sm font-medium text-green-600"
    : "text-sm font-medium text-red-600";
  const signButton = document.getElementById("sign-contract-button");
  let userHasSigned = false;
  if (currentUserId == transaction.buyer_id && contract.signed_by_buyer) {
    userHasSigned = true;
  }
  if (currentUserId == transaction.seller_id && contract.signed_by_seller) {
    userHasSigned = true;
  }

  if (userHasSigned) {
    signButton.disabled = true;
    signButton.textContent = "Bạn đã ký";
    signButton.classList.remove("bg-green-600", "hover:bg-green-700");
    signButton.classList.add("bg-gray-400", "cursor-not-allowed");
    signButton.onclick = null;
  } else {
    signButton.disabled = false;
    signButton.textContent = "Xác Nhận & Ký Hợp Đồng";
    signButton.classList.add("bg-green-600", "hover:bg-green-700");
    signButton.classList.remove("bg-gray-400", "cursor-not-allowed");
    signButton.onclick = () =>
      signContract(transaction.transaction_id, transaction);
  }
  document.getElementById("contract-loading-spinner").style.display = "none";
  document.getElementById("contract-content-wrapper").style.display = "block";
  openModal("contract-modal");
}
/** Ký hợp đồng giao dịch. */
async function signContract(transactionId, transaction) {
  const signButton = document.getElementById("sign-contract-button");
  signButton.disabled = true;
  signButton.textContent = "Đang ký...";
  showLoading();
  const currentUserId = getUserIdFromToken();

  try {
    // 1. Gọi API để ký
    const response = await apiRequest(
      `/transaction/api/transactions/${transactionId}/contract/sign`,
      "POST",
      {}, // Không cần body
      "transaction" // Chỉ định service 'transaction'
    );

    // 2. Xử lý phản hồi thành công
    if (response && response.contract) {
      showToast(response.message || "Ký hợp đồng thành công!");

      // 3. Cập nhật lại UI modal hợp đồng (chỉ trạng thái)
      const buyerStatus = document.getElementById("buyer-signature-status");
      const sellerStatus = document.getElementById("seller-signature-status");

      // Cập nhật trạng thái
      let buyerText = `Người mua: ${
        response.contract.signed_by_buyer ? "Đã ký" : "Chưa ký"
      }`;
      let sellerText = `Người bán: ${
        response.contract.signed_by_seller ? "Đã ký" : "Chưa ký"
      }`;
      if (currentUserId == transaction.buyer_id) buyerText += " (Bạn)";
      if (currentUserId == transaction.seller_id) sellerText += " (Bạn)";

      buyerStatus.textContent = buyerText;
      sellerStatus.textContent = sellerText;
      buyerStatus.className = response.contract.signed_by_buyer
        ? "text-sm font-medium text-green-600"
        : "text-sm font-medium text-red-600";
      sellerStatus.className = response.contract.signed_by_seller
        ? "text-sm font-medium text-green-600"
        : "text-sm font-medium text-red-600";

      // Vô hiệu hóa nút vì user này vừa ký xong
      signButton.disabled = true;
      signButton.textContent = "Bạn đã ký";
      signButton.classList.remove("bg-green-600", "hover:bg-green-700");
      signButton.classList.add("bg-gray-400", "cursor-not-allowed");
      signButton.onclick = null;
      if (
        response.contract.signed_by_buyer &&
        response.contract.signed_by_seller
      ) {
        showToast("Cả hai bên đã ký! Sẵn sàng thanh toán.", "success");
        closeModal("contract-modal");

        // Logic 4: Mở modal thanh toán (chỉ cho người mua)
        if (currentUserId == transaction.buyer_id) {
          // Truyền transaction (chứa final_price) vào
          openPaymentModal(transaction);
        } else {
          // Nếu là người bán, chỉ cần đóng modal và điều hướng
          navigateTo("transactions");
        }
      }
    } else {
      throw new Error(response.error || "Phản hồi ký không hợp lệ.");
    }
  } catch (error) {
    console.error("Lỗi khi ký hợp đồng:", error);
    showToast(`Lỗi: ${error.message}`, "error");
    // Kích hoạt lại nút nếu có lỗi
    signButton.disabled = false;
    signButton.textContent = "Xác Nhận & Ký Hợp Đồng";
  } finally {
    hideLoading();
  }
}
/** Mở form và thanh toán. */
function openPaymentModal(transaction) {
  document.getElementById("payment-transaction-id").value =
    transaction.transaction_id;

  const price = parseFloat(transaction.final_price) || 0;
  document.getElementById("payment-amount-display").dataset.amount = price;
  const formattedPrice = new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(price);

  document.getElementById("payment-amount-display").textContent =
    formattedPrice;

  // Reset form
  document.getElementById("payment-form").reset();
  document.getElementById("payment-method-select").value = "";

  // 🔍 Kiểm tra hợp đồng (để xác định có bật nút thanh toán không)
  apiRequest(
    `/transaction/api/transactions/${transaction.transaction_id}/contract`,
    "GET",
    null,
    "transaction"
  ).then((res) => {
    const payBtn = document.getElementById("confirm-payment-button");
    if (res && res.contract) {
      const bothSigned =
        res.contract.signed_by_buyer && res.contract.signed_by_seller;
      if (!bothSigned) {
        payBtn.disabled = true;
        payBtn.textContent = "Chờ hai bên ký xong";
        payBtn.classList.remove("bg-green-600", "hover:bg-green-700");
        payBtn.classList.add("bg-gray-400", "cursor-not-allowed");
      } else {
        payBtn.disabled = false;
        payBtn.textContent = "Xác nhận thanh toán";
        payBtn.classList.add("bg-green-600", "hover:bg-green-700");
        payBtn.classList.remove("bg-gray-400", "cursor-not-allowed");
      }
    }
  });

  openModal("payment-modal");
}

document
  .getElementById("payment-form")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const transactionId = document.getElementById(
      "payment-transaction-id"
    ).value;
    const method = document.getElementById("payment-method-select").value;
    const amount =
      parseFloat(
        document.getElementById("payment-amount-display").dataset.amount
      ) || 0;

    if (!method) {
      showToast("Vui lòng chọn phương thức thanh toán!", "error");
      return;
    }

    const payBtn = document.getElementById("confirm-payment-button");
    payBtn.disabled = true;
    payBtn.textContent = "Đang xử lý...";

    showLoading();

    try {
      const res = await apiRequest(
        `/transaction/api/transactions/${transactionId}/payment`,
        "POST",
        { payment_method: method, amount: amount },
        "transaction"
      );

      if (res && res.payment && !res.error) {
        showToast("Thanh toán thành công!", "success");
        closeModal("payment-modal");
        navigateTo("transactions");
      } else {
        throw new Error(res?.error || "Phản hồi không hợp lệ từ máy chủ.");
      }
    } catch (err) {
      console.error("Lỗi khi thanh toán:", err);
      showToast(`Lỗi khi thanh toán: ${err.message}`, "error");
      payBtn.disabled = false;
      payBtn.textContent = "Xác Nhận Thanh Toán";
    } finally {
      hideLoading();
    }
  });
/** Hiển thị trạng thái thanh toán giao dịch. */
async function openPaymentStatusModal(transactionId) {
  showLoading();
  // Lấy container chứa nút trước
  const actionContainer = document.getElementById("status-modal-actions");
  actionContainer.innerHTML = ""; // Xóa các nút cũ (nếu có)

  try {
    const res = await apiRequest(
      `/transaction/api/transactions/${transactionId}/payment/status`,
      "GET",
      null // Không cần service name nếu apiRequest tự xử lý
    );

    if (res && res.payment) {
      const p = res.payment; // Đây là paymentData

      // Điền thông tin vào modal như cũ
      document.getElementById(
        "status-transaction-id"
      ).textContent = `#${p.transaction_id}`;
      document.getElementById("status-payment-amount").textContent =
        new Intl.NumberFormat("vi-VN", {
          style: "currency",
          currency: "VND",
        }).format(p.amount || 0);
      document.getElementById("status-payment-method").textContent =
        formatPaymentMethod(p.payment_method);
      document.getElementById("status-payment-status").textContent =
        formatPaymentStatus(p.payment_status);
      document.getElementById("status-payment-status").className =
        getStatusColorClass(p.payment_status); 
      document.getElementById("status-payment-time").textContent = p.created_at
        ? new Date(p.created_at).toLocaleString("vi-VN")
        : "---";

      // --- THÊM LOGIC HIỂN THỊ NÚT ---
      if (p.payment_status === "completed") {
        actionContainer.innerHTML = `
                    <button data-transaction-id="${p.transaction_id}"
                            class="review-status-button bg-blue-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">
                        Đánh giá
                    </button>
                    <button data-transaction-id="${p.transaction_id}"
                            class="report-status-button bg-red-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50">
                        Báo cáo
                    </button>
                `;

        // Gắn sự kiện ngay lập tức cho các nút vừa tạo
        actionContainer
          .querySelector(".review-status-button")
          .addEventListener("click", () => {
            // Cần có buyer_id và seller_id trong 'p' để hàm này hoạt động
            if (p.buyer_id && p.seller_id) {
              closeModal("payment-status-modal"); // Đóng modal hiện tại
              openReviewModal(p.transaction_id, p); // Mở modal review
            } else {
              showToast("Thiếu thông tin buyer/seller để đánh giá.", "error");
              console.error(
                "Missing buyer_id/seller_id in payment status response:",
                p
              );
            }
          });
        actionContainer
          .querySelector(".report-status-button")
          .addEventListener("click", () => {
            // Cần có buyer_id và seller_id trong 'p' để hàm này hoạt động
            if (p.buyer_id && p.seller_id) {
              closeModal("payment-status-modal"); // Đóng modal hiện tại
              openReportModal(p.transaction_id, p); // Mở modal report
            } else {
              showToast("Thiếu thông tin buyer/seller để báo cáo.", "error");
              console.error(
                "Missing buyer_id/seller_id in payment status response:",
                p
              );
            }
          });
      } else {
        // Nếu không phải 'completed', đảm bảo không có nút nào
        actionContainer.innerHTML = "";
      }
      // ---------------------------------

      openModal("payment-status-modal"); // Mở modal sau khi đã chuẩn bị xong
    } else {
      // Sửa lại: Ném lỗi để catch xử lý chung
      throw new Error(res?.error || "Không tìm thấy thông tin thanh toán!");
    }
  } catch (err) {
    console.error("Lỗi khi xem tình trạng thanh toán:", err);
    // Hiển thị lỗi từ API hoặc lỗi mặc định
    showToast(
      err.message || "Có lỗi xảy ra khi tải trạng thái thanh toán.",
      "error"
    );
  } finally {
    hideLoading();
  }
}

// format hiển thị chữ
function formatPaymentMethod(method) {
  switch (method) {
    case "e-wallet":
      return "Ví điện tử";
    case "bank":
      return "Chuyển khoản ngân hàng";
    case "cash":
      return "Tiền mặt";
    default:
      return "Không xác định";
  }
}// format hiển thị chữ

function formatPaymentStatus(status) {
  switch (status) {
    case "initiated":
      return "Đang xử lý";
    case "completed":
      return "Hoàn tất";
    case "pending":
      return "Đã chuyển khoản Admin";
    case "failed":
      return "Thất bại";
    default:
      return "Không xác định";
  }
}
// format hiển thị chữ
function getStatusColorClass(status) {
  switch (status) {
    case "pending":
      return "text-base font-semibold text-yellow-600";
    case "completed":
      return "text-base font-semibold text-green-600";
    case "failed":
      return "text-base font-semibold text-red-600";
    default:
      return "text-base font-semibold text-gray-600";
  }
}
// lấy token
if (typeof getUserIdFromToken === "undefined") {
  function getUserIdFromToken() {
    const token = localStorage.getItem("jwt_token");
    if (!token) return null;
    try {
      const payloadBase64 = token.split(".")[1];
      const payload = JSON.parse(atob(payloadBase64));
      return Number(payload.sub);
    } catch (e) {
      console.error("Không thể giải mã token:", e);
      return null;
    }
  }
}
// Hiển thị các giao dịch với các trạng thái payment khác nhau
async function loadPaymentSections() {
  showLoading();
  const containers = [
    "initiated-container",
    "pending-container",
    "completed-container",
    "failed-container",
  ];
  containers.forEach((id) => {
    const container = document.getElementById(id);
    if (container) {
      container.innerHTML = `<div class="col-span-full text-center bg-white p-12 rounded-lg shadow"><p class="text-gray-500">Đang tải dữ liệu...</p></div>`;
    }
  });

  try {
    // 1. API trả về một danh sách các "Payments"
    const allPayments = await apiRequest("/transaction/api/my-transactions");

    // 2. Lưu trữ chúng dưới tên "allPaymentsData"
    window.allPaymentsData = Array.isArray(allPayments) ? allPayments : [];

    // 3. Lọc danh sách "Payments" (dùng 'p' cho payment)
    const initiated = window.allPaymentsData.filter(
      (p) => p.payment_status === "initiated"
    );
    const pending = window.allPaymentsData.filter(
      (p) => p.payment_status === "pending"
    );
    const completed = window.allPaymentsData.filter(
      (p) => p.payment_status === "completed"
    );
    const failed = window.allPaymentsData.filter(
      (p) => p.payment_status === "failed"
    );

    renderPaymentList(
      "initiated-container",
      initiated,
      "Bạn không có khoản nào chờ thanh toán."
    );
    renderPaymentList(
      "pending-container",
      pending,
      "Bạn không có khoản nào đang chờ duyệt."
    );
    renderPaymentList(
      "completed-container",
      completed,
      "Bạn không có giao dịch nào hoàn thành."
    );
    renderPaymentList(
      "failed-container",
      failed,
      "Bạn không có giao dịch nào thất bại."
    );
  } catch (error) {
    console.error("Failed to load payment sections:", error);
    renderPaymentList("initiated-container", [], "Không thể tải dữ liệu.");
    renderPaymentList("pending-container", [], "Không thể tải dữ liệu.");
    renderPaymentList("completed-container", [], "Không thể tải dữ liệu.");
    renderPaymentList("failed-container", [], "Không thể tải dữ liệu.");
  } finally {
    hideLoading();
  }
}
// ...
function getPaymentCardActions(payment) {
  switch (payment.payment_status) {
    case "initiated":
      return `
            <button data-transaction-id="${payment.transaction_id}" class="pay-pending-button bg-green-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50">
                Thanh Toán Ngay
            </button>`;
    case "pending":
      return `
            <div class="text-center">
                <p class="text-sm font-medium text-blue-600">Đang chờ duyệt</p>
                <p class="text-xs text-gray-500">(Đã thanh toán)</p>
            </div>`;
    case "completed":
      return `
            <div class="text-center space-y-2">
                <div>
                    <p class="text-sm font-medium text-green-600">Đã hoàn thành</p>
                    <p class="text-xs text-gray-500">(Admin đã duyệt)</p>
                </div>
                <div class="flex flex-col space-y-1">
                    <button data-transaction-id="${payment.transaction_id}" class="review-button bg-blue-500 text-white text-xs font-bold py-1 px-3 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">
                        Đánh giá
                    </button>
                    <button data-transaction-id="${payment.transaction_id}" class="report-button bg-red-500 text-white text-xs font-bold py-1 px-3 rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50">
                        Báo cáo
                    </button>
                </div>
            </div>`;
    case "failed":
      return `
            <div class="text-center">
                <p class="text-sm font-medium text-red-600">Thất bại</p>
                <button data-transaction-id="${payment.transaction_id}" class="retry-payment-button mt-2 bg-gray-500 text-white text-xs font-bold py-1 px-3 rounded hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-opacity-50">
                    Thử lại
                </button>
            </div>`;
    default:
      return `<p class="text-sm text-gray-500">${payment.payment_status}</p>`;
  }
}
// Hiển thị list payment
function renderPaymentList(containerId, payments, emptyMessage) {
  const container = document.getElementById(containerId);
  if (!container) return;

  if (!Array.isArray(payments) || payments.length === 0) {
    container.innerHTML = `
        <div class="col-span-full text-center bg-white p-12 rounded-lg shadow">
            <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H7a3 3 0 00-3 3v8a3 3 0 003 3z" />
            </svg>
            <h3 class="mt-2 text-sm font-medium text-gray-900">Danh sách trống</h3>
            <p class="mt-1 text-sm text-gray-500">${emptyMessage}</p>
        </div>`;
    return;
  }

  container.innerHTML = payments
    .map((p) => {
      const formattedPrice =
        parseFloat(p.amount).toLocaleString("vi-VN") + " VNĐ";
      const formattedDate = new Date(p.created_at).toLocaleDateString("vi-VN");

      const imageUrl = p.listing_image
        ? apiBaseUrl + p.listing_image
        : "https://placehold.co/400x400/e2e8f0/e2e8f0?text=Giao+dịch";

      return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden flex items-center">
            <div class="w-32 h-32 flex-shrink-0 bg-gray-200">
                <img src="${imageUrl}" alt="Sản phẩm" class="w-full h-full object-cover">
            </div>
            <div class="p-4 flex-grow">
                <p class="text-sm text-gray-500">Giao dịch #${
                  p.transaction_id
                }</p> 
                <p class="text-sm text-gray-500">Phương thức: ${
                  p.payment_method
                }</p>
                <p class="text-indigo-600 font-bold text-xl">${formattedPrice}</p>
                <p class="text-sm text-gray-500 mt-2">Ngày tạo: ${formattedDate}</p>
            </div>
            <div class="p-4 w-40 flex-shrink-0 flex justify-center items-center">
                ${getPaymentCardActions(p)} </div>
        </div>
        `;
    })
    .join("");

  const handlePaymentClick = (event) => {
    const button = event.currentTarget;
    const transactionId = button.dataset.transactionId;

    const paymentToPay = window.allPaymentsData.find(
      (p) => p.transaction_id == transactionId
    );

    if (paymentToPay) {
      initiatePendingPayment(paymentToPay, button);
    } else {
      console.error("Không tìm thấy dữ liệu thanh toán cho ID:", transactionId);
      showToast("Lỗi: Không tìm thấy dữ liệu thanh toán.", "error");
    }
  };
  const handleReviewClick = (event) => {
    const button = event.currentTarget;
    const transactionId = button.dataset.transactionId;
    console.log("Review button clicked for transaction:", transactionId);
    const paymentData = window.allPaymentsData.find(
      (p) => p.transaction_id == transactionId
    );
    if (paymentData) {
      openReviewModal(transactionId, paymentData);
    } else {
      showToast(
        "Lỗi: Không tìm thấy thông tin giao dịch để đánh giá.",
        "error"
      );
    }
  };

  const handleReportClick = (event) => {
    const button = event.currentTarget;
    const transactionId = button.dataset.transactionId;
    console.log("Report button clicked for transaction:", transactionId);
    const paymentData = window.allPaymentsData.find(
      (p) => p.transaction_id == transactionId
    );
    if (paymentData) {
      openReportModal(transactionId, paymentData);
    } else {
      showToast("Lỗi: Không tìm thấy thông tin giao dịch để báo cáo.", "error");
    }
  };

  container.querySelectorAll(".pay-pending-button").forEach((button) => {
    button.addEventListener("click", handlePaymentClick);
  });
  container.querySelectorAll(".retry-payment-button").forEach((button) => {
    button.addEventListener("click", handlePaymentClick);
  });
  container.querySelectorAll(".review-button").forEach((button) => {
    button.addEventListener("click", handleReviewClick);
  });
  container.querySelectorAll(".report-button").forEach((button) => {
    button.addEventListener("click", handleReportClick);
  });
}


async function initiatePendingPayment(transaction, clickedButton) {
  if (!transaction) {
    showToast("Lỗi: Không có dữ liệu giao dịch.", "error");
    return;
  }

  let originalButtonText = "Thanh Toán Ngay";
  if (clickedButton) {
    originalButtonText = clickedButton.textContent;
    clickedButton.disabled = true;
    clickedButton.textContent = "Đang xử lý...";
  }

  showLoading();

  try {
    const transactionId = transaction.transaction_id;
    const response = await apiRequest(
      `/transaction/api/transactions/${transactionId}/confirm-payment`,
      "POST",
      { payment_method: transaction.payment_method }
    );

    if (response && response.payment_url) {
      window.location.href = response.payment_url;
    } else {
      throw new Error(response.error || "Không thể khởi tạo thanh toán.");
    }
  } catch (error) {
    console.error("Lỗi khi tạo thanh toán:", error);
    showToast(`Lỗi: ${error.message}`, "error");

    if (clickedButton) {
      clickedButton.disabled = false;
      clickedButton.textContent = originalButtonText;
    }
  } finally {
    hideLoading();
  }
}
// dợi lấy trạng thái thanh toán
function pollPaymentStatus(
  transactionId,
  startTime = Date.now(),
  maxWaitTime = 30000
) {
  return new Promise(async (resolve, reject) => {
    try {
      const response = await apiRequest(
        `/transaction/api/transactions/${transactionId}/payment-status`,
        "GET"
      );

      if (response && response.status) {
        if (response.status === "pending" || response.status === "failed") {
          resolve(response.status);
        } else {
          if (Date.now() - startTime > maxWaitTime) {
            reject(
              new Error("Kiểm tra trạng thái quá lâu. Vui lòng tải lại trang.")
            );
          } else {
            setTimeout(() => {
              pollPaymentStatus(transactionId, startTime, maxWaitTime)
                .then(resolve)
                .catch(reject);
            }, 2000);
          }
        }
      } else {
        throw new Error(
          response.error || "Không thể lấy trạng thái giao dịch."
        );
      }
    } catch (error) {
      // Lỗi khi gọi API
      reject(error);
    }
  });
}
// hiển thị kết quả thanh toán
async function loadPaymentResult() {
  const successIcon = `...`;
  const failIcon = `...`;
  const loadingIcon = `<svg class="animate-spin h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>`;

  const iconEl = document.getElementById("result-icon-container");
  const titleEl = document.getElementById("result-payment-title");
  const messageEl = document.getElementById("result-payment-message");
  const detailsEl = document.getElementById("result-payment-details");

  titleEl.classList.remove("text-green-600", "text-red-600", "text-gray-700");

  let urlParams;
  let transactionId;
  let orderId;
  let amount;
  let finalStatus;
  let displayMessage;

  try {
    let queryString = "";
    if (window.location.hash.includes("?")) {
      queryString = window.location.hash.split("?")[1];
    } else if (window.location.search) {
      queryString = window.location.search.slice(1);
    }
    urlParams = new URLSearchParams(queryString);
    orderId = urlParams.get("orderId");
    amount = urlParams.get("amount");
    displayMessage = urlParams.get("message") || "Không có thông báo.";

    if (!orderId) {
      throw new Error("Không tìm thấy orderId trong URL.");
    }

    transactionId = parseInt(orderId.split("-")[0], 10);
    if (isNaN(transactionId)) {
      throw new Error("Định dạng orderId không hợp lệ.");
    }
    iconEl.innerHTML = loadingIcon;
    titleEl.textContent = "Đang xác nhận thanh toán...";
    titleEl.classList.add("text-gray-700");
    messageEl.textContent =
      "Vui lòng chờ. Hệ thống đang xác nhận với máy chủ...";

    let tempDetails = `<div><strong>Mã giao dịch:</strong> #${transactionId}</div>`;
    if (amount) {
      const formattedAmount = new Intl.NumberFormat("vi-VN").format(amount);
      tempDetails += `<div><strong>Số tiền:</strong> ${formattedAmount} VNĐ</div>`;
    }
    detailsEl.innerHTML = tempDetails;
    finalStatus = await pollPaymentStatus(transactionId);
  } catch (error) {
    console.error("Lỗi khi xử lý kết quả thanh toán:", error);
    finalStatus = "failed";
    displayMessage = error.message || "Không thể xác nhận giao dịch.";
  }

  titleEl.classList.remove("text-gray-700");

  if (finalStatus === "pending") {
    iconEl.innerHTML = successIcon;
    titleEl.textContent = "Thanh toán thành công!";
    titleEl.classList.add("text-green-600");
    messageEl.textContent = decodeURIComponent(displayMessage).replace(
      /\+/g,
      " "
    );
  } else {
    iconEl.innerHTML = failIcon;
    titleEl.textContent = "Thanh toán thất bại!";
    titleEl.classList.add("text-red-600");
    messageEl.textContent = decodeURIComponent(displayMessage).replace(
      /\+/g,
      " "
    );
  }

  let detailsHTML = "";
  if (orderId) {
    const originalOrderId = orderId.split("-")[0];
    detailsHTML += `<div><strong>Mã giao dịch:</strong> #${originalOrderId}</div>`;
  }
  if (amount) {
    const formattedAmount = new Intl.NumberFormat("vi-VN").format(amount);
    detailsHTML += `<div><strong>Số tiền:</strong> ${formattedAmount} VNĐ</div>`;
  }
  const resultCode =
    urlParams.get("resultCode") || (finalStatus === "completed" ? "0" : "99");
  detailsHTML += `<div><strong>Mã kết quả:</strong> ${resultCode}</div>`;

  detailsEl.innerHTML = detailsHTML;
}
// tải ảnh
function uploadImage(id, listing_type) {
  const modal = document.getElementById("upload-modal");
  modal.classList.remove("hidden");
  modal.dataset.id = id;
  modal.dataset.type = listing_type;
  const fileInput = document.getElementById("upload-image-input");
  if (fileInput) fileInput.value = null;
}

/** Xác nhận và gửi ảnh lên server. */
async function confirmUpload() {
  const modal = document.getElementById("upload-modal");
  const fileInput = document.getElementById("upload-image-input");
  try {
    const id = modal.dataset.id;
    const listing_type = modal.dataset.type;
    const file = fileInput.files[0];
    if (!file) {
      alert("Vui lòng chọn một ảnh!");
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    let uploadUrl = "";
    if (listing_type === "vehicle") {
      uploadUrl = `/listing/api/listings/add_image_vehicle/${id}`;
    } else if (listing_type === "battery") {
      uploadUrl = `/listing/api/listings/add_image_battery/${id}`;
    } else {
      alert("Loại listing không hợp lệ!");
      return;
    }
    const res = await fetch(`${apiBaseUrl}${uploadUrl}`, {
      method: "POST",
      body: formData,
      headers: {
        Authorization: `Bearer ${localStorage.getItem("jwt_token")}`,
      },
    });
    const data = await res.json();
    if (!res.ok) {
      alert(`Lỗi: ${data.error || res.statusText}`);
      return;
    }
    closeAdd("upload-modal");
    closeModal("detail-modal");
    showToast("Tải ảnh thành công!");
    loadMyAssets();
  } catch (err) {
    console.error("Upload error:", err);
    alert("Lỗi khi tải ảnh lên!");
  } finally {
    fileInput.value = null;
  }
}















function showMarketTab(tabName) {
  const listingsContainer = document.getElementById("listings-container");
  const auctionsContainer = document.getElementById("auctions-container");
  const listingTab = document.getElementById("listing-tab");
  const auctionTab = document.getElementById("auction-tab");

  const listingFilters = document.getElementById("listing-filters");
  const vehicleFilters = document.getElementById("vehicle-filters");
  const batteryFilters = document.getElementById("battery-filters");
  const auctionFilters = document.getElementById("auction-filters");

  if (
    !listingsContainer ||
    !auctionsContainer ||
    !listingTab ||
    !auctionTab ||
    !listingFilters ||
    !auctionFilters
  )
    return;

  // Reset tất cả tab về trạng thái mặc định
  [listingTab, auctionTab].forEach((tab) => {
    tab.classList.remove("border-indigo-500", "text-indigo-600");
    tab.classList.add(
      "border-transparent",
      "text-gray-500",
      "hover:text-gray-700",
      "hover:border-gray-300"
    );
  });

  // Kiểm tra tab hiện tại
  const isListing = tabName === "listings";

  // Ẩn/hiện container dữ liệu
  listingsContainer.classList.toggle("hidden", !isListing);
  auctionsContainer.classList.toggle("hidden", isListing);

  // Ẩn/hiện phần bộ lọc tương ứng
  listingFilters.classList.toggle("hidden", !isListing);
  vehicleFilters.classList.toggle("hidden", true);
  batteryFilters.classList.toggle("hidden", true);
  auctionFilters.classList.toggle("hidden", isListing);

  // Kích hoạt tab đang chọn
  const activeTab = isListing ? listingTab : auctionTab;
  activeTab.classList.add("border-indigo-500", "text-indigo-600");
  activeTab.classList.remove(
    "border-transparent",
    "text-gray-500",
    "hover:text-gray-700",
    "hover:border-gray-300"
  );
}


// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  updateNav();
  const token = localStorage.getItem("jwt_token");

  let isLoggedIn = false;
  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      if (payload.exp && payload.exp >= currentTime) {
        isLoggedIn = true;
      } else {
        localStorage.removeItem("jwt_token");
      }
    } catch (e) {
      localStorage.removeItem("jwt_token");
    }
  }

  const isPaymentResultPath =
    window.location.pathname.includes("/payment-result");
  const isPaymentResultHash =
    window.location.hash.startsWith("#/payment-result");

  // 3. Kiểm tra xem điều kiện có đúng không
  if (isPaymentResultPath || isPaymentResultHash) {
    navigateTo("payment-result");
    loadPaymentResult();
    window.history.replaceState({}, document.title, "/#");
  } else {
    // 5. Log nếu điều kiện SAI
    if (isLoggedIn) {
      navigateTo("profile");
    } else {
      navigateTo("home");
    }
  }
});


async function loadMyReviewsAndReports() {
    // Đặt trạng thái loading
    const writtenContainer = document.getElementById("my-written-reviews-container");
    const aboutMeContainer = document.getElementById("reviews-about-me-container");
    const reportsContainer = document.getElementById("my-filed-reports-container");

    // Kiểm tra container tồn tại trước khi gán innerHTML
    if (writtenContainer) writtenContainer.innerHTML = `<p class="text-gray-500">Đang tải...</p>`;
    if (aboutMeContainer) aboutMeContainer.innerHTML = `<p class="text-gray-500">Đang tải...</p>`;
    if (reportsContainer) reportsContainer.innerHTML = `<p class="text-gray-500">Đang tải...</p>`;

    const currentUserId = getUserIdFromToken();
    if (!currentUserId) {
         showToast("Lỗi xác thực, vui lòng đăng nhập lại.", "error");
         return;
    }

    try {
        // Gọi 3 API song song để tải dữ liệu nhanh hơn
        const [writtenReviews, reviewsAboutMe, myReports] = await Promise.all([
            // Gọi API "Đánh giá bạn đã viết"
            apiRequest('/review/api/reviews/my-reviews', 'GET', null, 'review'), 
            // Gọi API "Đánh giá về bạn"
            apiRequest(`/review/api/reviews/user/${currentUserId}`, 'GET', null, 'review'), 
            // Gọi API "Báo cáo bạn đã gửi" (Bạn cần tạo endpoint này bên report-service)
            apiRequest('/report/api/reports/my-reports', 'GET', null, 'report') 
        ]);

        // Render kết quả vào các container
        renderMyWrittenReviews(writtenReviews);
        renderReviewsAboutMe(reviewsAboutMe);
        renderMyFiledReports(myReports);

    } catch (error) {
        console.error("Lỗi khi tải đánh giá và báo cáo:", error);
        showToast("Không thể tải dữ liệu đánh giá/báo cáo.", "error");
        if (writtenContainer) writtenContainer.innerHTML = `<p class="text-red-500">Lỗi tải dữ liệu.</p>`;
        if (aboutMeContainer) aboutMeContainer.innerHTML = `<p class="text-red-500">Lỗi tải dữ liệu.</p>`;
        if (reportsContainer) reportsContainer.innerHTML = `<p class="text-red-500">Lỗi tải dữ liệu.</p>`;
    }
}
