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
  document.getElementById(id).classList.add('hidden');
}
 
const closeModal = (modalId) =>
  document.getElementById(modalId).classList.remove("active");
 
const openModal = (modalId, data = {}) => {
    const modal = document.getElementById(modalId);
    if (!modal) {
        console.error(`Modal with id "${modalId}" not found.`);
        return;
    }
    const form = modal.querySelector('form');
    if (form) {
        form.reset();
        if (modalId === "vehicle-modal") {
            document.getElementById("vehicle-modal-title").textContent = data.vehicle_id
                ? "Sửa thông tin Xe"
                : "Thêm Xe Mới";
            document.getElementById("vehicle-id").value = data.vehicle_id || "";
            document.getElementById("vehicle-brand").value = data.brand || "";
            document.getElementById("vehicle-model").value = data.model || "";
            document.getElementById("vehicle-year").value = data.year || "";
            document.getElementById("vehicle-mileage").value = data.mileage || "";
        } else if (modalId === "battery-modal") {
            document.getElementById("battery-modal-title").textContent = data.battery_id
                ? "Sửa thông tin Pin"
                : "Thêm Pin Mới";
            document.getElementById("battery-id").value = data.battery_id || "";
            document.getElementById("battery-manufacturer").value =
            data.manufacturer || "";
            document.getElementById("battery-capacity").value = data.capacity_kwh || "";
            document.getElementById("battery-health").value = data.health_percent || "";
        } else if (modalId === "listing-modal") {
            document.getElementById("listing-item-id").value = data.id || "";
            document.getElementById("listing-item-type").value = data.type || "";
        } else if (modalId === "auction-modal") {
            document.getElementById("auction-item-id").value = data.id || "";
            document.getElementById("auction-item-type").value = data.type || "";

            // Tự động đặt thời gian bắt đầu mặc định là 8.5 giờ kể từ bây giờ
            const defaultStartTime = new Date(Date.now() + 8.5 * 60 * 60 * 1000);
            const y = defaultStartTime.getFullYear();
            const m = (defaultStartTime.getMonth() + 1).toString().padStart(2, '0');
            const d = defaultStartTime.getDate().toString().padStart(2, '0');
            const h = defaultStartTime.getHours().toString().padStart(2, '0');
            const min = defaultStartTime.getMinutes().toString().padStart(2, '0');
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
 
function isLoggedIn() {
    return !!localStorage.getItem('jwt_token');
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
    if (pageId === "watchlist"){
        loadMyWatchlist();
    }
    if (pageId === "listings") {
        loadPublicListings();
        loadPublicAuctions();
        showMarketTab('listings');
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
        <p><strong>Điện thoại:</strong> ${data.phone_number || "Chưa cập nhật"}</p>
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
    const form = document.getElementById('profile-update-form');
    const buttonContainer = document.getElementById('update-profile-button-container');

    if (!form || !buttonContainer) return;

    if (forceShow === true) {
        form.classList.remove('hidden');
        buttonContainer.classList.add('hidden');
    } else if (forceShow === false) {
        form.classList.add('hidden');
        buttonContainer.classList.remove('hidden');
    } else {
        form.classList.toggle('hidden');
        buttonContainer.classList.toggle('hidden');
    }
}


// --- AUTH & PROFILE EVENT LISTENERS ---

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email_username = document.getElementById("login-email-username").value;
  const password = document.getElementById("login-password").value;
  try {
    const data = await apiRequest("/user/api/login", "POST", { email_username, password });
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

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("register-username").value;
  const email = document.getElementById("register-email").value;
  const password = document.getElementById("register-password").value;
  try {
    const data = await apiRequest("/user/api/register", "POST", { username, email, password });
    if (data) {
      showToast(data.message || "Đăng ký thành công! Vui lòng đăng nhập.");
      navigateTo("login");
    }
  } catch (error) {}
});

document.getElementById("forget-password-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("forget-email").value;
  try {
    const data = await apiRequest("/user/api/send-otp", "POST", { email });
    if (data) {
      showToast(data.message || "OTP đã được gửi đến email của bạn.");
      document.getElementById("forget-password-form").classList.add("hidden");
      document.getElementById("reset-password-form").classList.remove("hidden");
    }
  } catch (error) {}
});

document.getElementById("reset-password-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = document.getElementById("forget-email").value;
  const otp = document.getElementById("otp-code").value;
  const new_password = document.getElementById("new-password").value;
  try {
    const data = await apiRequest("/user/api/reset-password", "POST", { email, otp, new_password });
    if (data) {
      showToast(data.message || "Mật khẩu đã được đặt lại thành công!");
      navigateTo("login");
    }
  } catch (error) {}
});

document.getElementById("profile-update-form").addEventListener("submit", async (e) => {
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
        allMyVehicles = (vehicles && Array.isArray(vehicles)) ? vehicles : [];
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
        allMyBatteries = (batteries && Array.isArray(batteries)) ? batteries : [];
        renderMyBatteries();
    } catch (error) {
        console.error("Failed to load batteries:", error);
        allMyBatteries = [];
        renderMyBatteries();
    }
}
 
// Giả sử bạn có hàm renderMyVehicles như thế này
function renderMyVehicles(showAll = false) {
    const container = document.getElementById('my-vehicles-container'); // Thay bằng ID container của bạn
    if (!container) return;

    const vehiclesToDisplay = showAll ? allMyVehicles : allMyVehicles.slice(0, 2);

    // Nếu không có xe nào, hiển thị thông báo
    if (allMyVehicles.length === 0) {
        container.innerHTML = '<p class="text-center text-gray-500">Bạn chưa có xe nào.</p>';
        return;
    }

    let contentHTML = vehiclesToDisplay.map(v => {
        // Sử dụng if/else if/else để code dễ đọc hơn khi có nhiều điều kiện
        let statusBadge = '';
        let detailInfo = '';
        let primaryActions = '';
        // Mặc định cho phép sửa/xóa
        let secondaryActions = `
            <button onclick='openModal("vehicle-modal", ${JSON.stringify(v)})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
            <button onclick="deleteVehicle(${v.vehicle_id})" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button>
        `;
        if (v.is_auctioned) {
            // --- 1. Trường hợp ĐANG ĐẤU GIÁ ---
            statusBadge = `<span class="ml-2 bg-purple-200 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">Đang đấu giá</span>`;
            // Có thể dẫn đến trang chi tiết đấu giá
            detailInfo = `<button onclick="viewVehicleAuctionDetail('${v.vehicle_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
            primaryActions = `<button onclick="unauctionVehicle('${v.vehicle_id}')" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gỡ Đấu Giá</button>`;
            // Không cho phép Sửa/Xóa khi đang đấu giá
            secondaryActions = ''; 
        } else if (v.is_listed) {
            // --- 2. Trường hợp ĐANG ĐĂNG BÁN (nhưng không đấu giá) ---
            statusBadge = renderStatusBadge(v.listing_status); // Dùng lại hàm renderStatusBadge của bạn
            detailInfo = `<button onclick="viewVehicleDetail('${v.vehicle_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem Chi Tiết</button>`;
            primaryActions = `<button onclick="unlistVehicle(${v.vehicle_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`;
            // Vẫn cho phép Sửa/Xóa khi chỉ đăng bán
        } else {
            // --- 3. Trường hợp CHƯA LÀM GÌ ---
            detailInfo = `Dòng xe: ${v.model} | Số KM: ${v.mileage.toLocaleString()}`;
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
    }).join("");

    if (allMyVehicles.length > 2) {
        contentHTML += `
            <div class="text-center mt-4">
                <button onclick="renderMyVehicles(${!showAll})" class="text-blue-600 hover:underline font-semibold">
                    ${showAll ? 'Ẩn bớt' : `Hiển thị toàn bộ (${allMyVehicles.length})`}
                </button>
            </div>`;
    }

    container.innerHTML = contentHTML;
}
 
/**
 * Hiển thị danh sách pin của người dùng ra giao diện.
 * @param {boolean} showAll - True để hiển thị tất cả, false để chỉ hiển thị 2 pin đầu.
 */
function renderMyBatteries(showAll = false) {
    const container = document.getElementById("my-batteries-container");
    if (!container) return;

    if (!allMyBatteries || allMyBatteries.length === 0) {
        container.innerHTML = `<p class="text-center text-gray-500">Bạn chưa có pin nào.</p>`;
        return;
    }

    const batteriesToDisplay = showAll ? allMyBatteries : allMyBatteries.slice(0, 2);
    let contentHTML = batteriesToDisplay.map(b => {
        // Tách logic ra các biến để code dễ đọc hơn
        let statusBadge = '';
        let detailInfo = '';
        let primaryActions = '';
        // Mặc định cho phép Sửa/Xóa
        let secondaryActions = `
            <button onclick='openModal("battery-modal", ${JSON.stringify(b)})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
            <button onclick="deleteBattery(${b.battery_id})" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button>
        `;

        if (b.is_auctioned) {
            // --- 1. Trường hợp ĐANG ĐẤU GIÁ ---
            statusBadge = `<span class="ml-2 bg-purple-200 text-purple-800 text-xs font-semibold px-2.5 py-0.5 rounded-full">Đang đấu giá</span>`;
            detailInfo = `<button onclick="viewBatteryAuctionDetail('${b.battery_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem chi tiết đấu giá</button>`;
            primaryActions = `<button onclick="unauctionBattery('${b.battery_id}')" class="bg-purple-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-purple-600">Gỡ Đấu Giá</button>`;
            // Không cho phép Sửa/Xóa khi đang đấu giá
            secondaryActions = ''; 
        } else if (b.is_listed) {
            // --- 2. Trường hợp ĐANG ĐĂNG BÁN (nhưng không đấu giá) ---
            statusBadge = renderStatusBadge(b.listing_status);
            detailInfo = `<button onclick="viewBatteryDetail('${b.battery_id}')" class="text-gray-400 text-[0.6rem] rounded hover:text-indigo-600">Xem Chi Tiết</button>`;
            primaryActions = `<button onclick="unlistBattery(${b.battery_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`;
        } else {
            // --- 3. Trường hợp CHƯA LÀM GÌ ---
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
    }).join("");

    if (allMyBatteries.length > 2) {
        contentHTML += `<div class="text-center mt-4">
            <button onclick="renderMyBatteries(${!showAll})" class="text-blue-600 hover:underline font-semibold">
                ${showAll ? 'Ẩn bớt' : `Hiển thị toàn bộ (${allMyBatteries.length})`}
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

document.getElementById("vehicle-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("vehicle-id").value;
  const body = {
    brand: document.getElementById("vehicle-brand").value,
    model: document.getElementById("vehicle-model").value,
    year: parseInt(document.getElementById("vehicle-year").value),
    mileage: parseInt(document.getElementById("vehicle-mileage").value),
  };

  const method = id ? "PUT" : "POST";
  const endpoint = id ? `/listing/api/my-assets/vehicles/${id}` : "/listing/api/my-assets/vehicles";

  try {
    await apiRequest(endpoint, method, body);
    showToast(id ? "Cập nhật xe thành công." : "Thêm xe mới thành công.");
    closeModal("vehicle-modal");
    loadMyVehicles();
  } catch (error) {}
});

document.getElementById("battery-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("battery-id").value;
  const body = {
    manufacturer: document.getElementById("battery-manufacturer").value,
    capacity_kwh: parseFloat(document.getElementById("battery-capacity").value),
    health_percent: parseInt(document.getElementById("battery-health").value),
  };

  const method = id ? "PUT" : "POST";
  const endpoint = id ? `/listing/api/my-assets/batteries/${id}` : "/listing/api/my-assets/batteries";

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

/** Tải và hiển thị tất cả các tin đăng bán công khai. */
async function loadPublicListings() {
  try {
    const listings = await apiRequest("/listing/api/listings");
    const container = document.getElementById("listings-container");

    if (listings && Array.isArray(listings) && listings.length > 0) {
      container.innerHTML = listings.map((item) => {
          let detailsHtml = "";
          if (item.listing_type === "vehicle" && item.vehicle_details) {
            const v = item.vehicle_details;
            detailsHtml = `
              <p class="text-gray-600">Hãng xe: ${v.brand} | Dòng xe: ${v.model} | Năm sản xuất: ${v.year}</p>
              <p class="text-sm text-gray-500">Số KM: ${v.mileage.toLocaleString()}</p>
            `;
          } else if (item.listing_type === "battery" && item.battery_details) {
            const b = item.battery_details;
            detailsHtml = `
              <p class="text-gray-600">Nhà sản xuất: ${b.manufacturer}</p>
              <p class="text-sm text-gray-500">${b.capacity_kwh}kWh | Tình trạng: ${b.health_percent}%</p>
            `;
          }

          return `
            <div class="bg-white rounded-lg shadow-md overflow-hidden flex flex-col transition-transform transform hover:-translate-y-1">
              <div class="relative w-full h-48 bg-gray-200">
                <img src="${item.images[0] ? apiBaseUrl + item.images[0] : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+"}"
                     alt="${item.title}" class="w-full h-full object-cover">
              </div>
              <div class="p-4 flex flex-col flex-grow">
                <h3 class="font-bold text-lg mb-2 truncate">${item.title}</h3>
                <div class="flex-grow mb-4">${detailsHtml}</div>
                <div class="mt-auto flex justify-between items-center">
                  <p class="text-indigo-600 font-bold text-xl">${Number(item.price * (item.listing_type == "vehicle" ? 1.1 : 1.05)).toLocaleString()} VNĐ</p>
                  <div class="flex items-center space-x-2">
                    <button onclick="addToWatchlist(${item.listing_id})" title="Thêm vào danh sách theo dõi" class="text-gray-400 hover:text-teal-500 p-2 rounded-full hover:bg-gray-100 transition duration-300">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                    </button>
                    <button onclick="viewDetail('${item.listing_id}')" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                  </div>
                </div>
              </div>
            </div>
          `;
        }).join("");
    } else {
      container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-gray-600">Hiện chưa có tin đăng nào.</p></div>`;
    }
  } catch (error) {
    const container = document.getElementById("listings-container");
    container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách tin đăng. Vui lòng thử lại.</p></div>`;
  }
}

// --- LISTING FORM EVENT LISTENER ---

document.getElementById("listing-form").addEventListener("submit", async (e) => {
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
  openModal('auction-modal', { type, id });
}

/** Tải và hiển thị các phiên đấu giá công khai. */


// --- AUCTION FORM EVENT LISTENER ---

document.getElementById("auction-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const id = document.getElementById("auction-item-id").value;
    const type = document.getElementById("auction-item-type").value;
    const startTime = document.getElementById("auction-start-time").value;
    const startBid = parseFloat(document.getElementById("auction-start-bid").value);

    if (!startTime || !startBid || startBid <= 0) {
        showToast("Vui lòng nhập ngày bắt đầu và giá khởi điểm hợp lệ.", true);
        return;
    }

    const body = {
        auction_type: type,
        start_time: new Date(startTime).toISOString(),
        current_bid: startBid
    };

    if (type === 'vehicle') {
        body.vehicle_id = parseInt(id);
    } else if (type === 'battery') {
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

        container.innerHTML = listings.map(listing => {
            let detailsHtml = "";
            if (listing.listing_type === "vehicle" && listing.vehicle_details) {
                const v = listing.vehicle_details;
                detailsHtml = `
                    <p class="text-gray-600">Hãng xe: ${v.brand} | Dòng xe: ${v.model} | Năm sản xuất: ${v.year}</p>
                    <p class="text-sm text-gray-500">Số KM: ${v.mileage.toLocaleString()}</p>`;
            } else if (listing.listing_type === "battery" && listing.battery_details) {
                const b = listing.battery_details;
                detailsHtml = `
                    <p class="text-gray-600">Nhà sản xuất: ${b.manufacturer}</p>
                    <p class="text-sm text-gray-500">${b.capacity_kwh}kWh | Tình trạng: ${b.health_percent}%</p>`;
            }

            const imageUrl = listing.images && listing.images.length > 0 ? apiBaseUrl + listing.images[0] : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+";
            const formattedPrice = parseFloat(listing.price).toLocaleString('vi-VN') + " VNĐ";

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
                            <button onclick="viewDetail('${listing.listing_id}')" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                        </div>
                    </div>
                </div>
            </div>`;
        }).join("");

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

/**
 * Thêm một sản phẩm vào danh sách theo dõi.
 * @param {number} listingId - ID của tin đăng cần thêm.
 */
async function addToWatchlist(listingId) {
    if (!isLoggedIn()) {
        alert("Bạn phải đăng nhập để sử dụng chức năng này.");
        navigateTo('login');
        return;
    }
    showLoading();
    try {
        const response = await apiRequest(`/listing/api/watch-list`, "POST", { listing_id: listingId });
        showToast(response.message || "Đã thêm vào danh sách theo dõi thành công!");
    } catch (error) {
        console.log("Thao tác thêm vào watchlist không thành công.");
    } finally {
        hideLoading();
    }
}
 
async function removeFromWatchlist(buttonElement, listingId) {
    if (!confirm("Bạn có chắc muốn bỏ theo dõi tin đăng này?")) {
        return;
    }
    showLoading();
    try {
        await apiRequest(`/listing/api/watch-list/by-listing/${listingId}`, 'DELETE');
        showToast("Đã bỏ theo dõi thành công.");
        const card = buttonElement.closest('.bg-white.rounded-lg.shadow-md');
        if (card) {
            card.style.transition = 'opacity 0.5s ease';
            card.style.opacity = '0';
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
async function viewDetail(listingId) {
    const modalContent = document.getElementById('detail-modal-content');
    modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
    document.getElementById('add-image-btn')?.remove();
    openModal('detail-modal');

    try {
        const listing = await apiRequest(`/listing/api/listings/${listingId}`);
        if (listing) {
            renderListingDetail(listing);
        } else {
           modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
        }
    } catch (error) {
       modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
    }
}

/** Hiển thị chi tiết một chiếc xe từ kho cá nhân. */
async function viewVehicleDetail(vehicle_id) {
  const modalContent = document.getElementById('detail-modal-content');
  modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
  const buttonDiv = document.getElementById('button_div');
  let btn = document.getElementById('add-image-btn');
  if (!btn) {
      btn = document.createElement('button');
      btn.id = 'add-image-btn';
      btn.textContent = 'Cập nhật ảnh';
      btn.className = 'bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600';
      buttonDiv.prepend(btn);
  }
  btn.onclick = () => uploadImage(vehicle_id, 'vehicle');
  openModal('detail-modal');
  try {
    const listing = await apiRequest(`/listing/api/listings/vehicle/${vehicle_id}`);
    if (listing) {
      renderListingDetail(listing);
    } else {
      modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
    }
  } catch (error) {
    modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
  }
}

/** Hiển thị chi tiết một viên pin từ kho cá nhân. */
async function viewBatteryDetail(battery_id) {
    const modalContent = document.getElementById('detail-modal-content');
    modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
    const buttonDiv = document.getElementById('button_div');
    let btn = document.getElementById('add-image-btn');
    if (!btn) {
        btn = document.createElement('button');
        btn.id = 'add-image-btn';
        btn.textContent = 'Cập nhật ảnh';
        btn.className = 'bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600';
        buttonDiv.prepend(btn);
    }
    btn.onclick = () => uploadImage(battery_id, 'battery');
    openModal('detail-modal');
    try {
        const listing = await apiRequest(`/listing/api/listings/battery/${battery_id}`);
        if (listing) {
            renderListingDetail(listing);
        } else {
            modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết tin đăng.</p>';
        }
    } catch (error) {
        modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
    }
}

/** Render nội dung HTML cho modal chi tiết tin đăng. */
function renderListingDetail(item) {
    const modalContent = document.getElementById('detail-modal-content');
    let productDetailsHtml = '';
    if (item.listing_type === 'vehicle' && item.vehicle_details) {
        const v = item.vehicle_details;
        productDetailsHtml = `
            <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                <p><strong>Hãng xe:</strong> ${v.brand}</p>
                <p><strong>Dòng xe:</strong> ${v.model}</p>
                <p><strong>Năm sản xuất:</strong> ${v.year}</p>
                <p><strong>Số KM đã đi:</strong> ${v.mileage.toLocaleString()}</p>
            </div>`;
    } else if (item.listing_type === 'battery' && item.battery_details) {
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
        <p class="text-2xl font-bold text-indigo-600 mb-4">Giá: ${Number(item.price).toLocaleString()} VNĐ</p>
        <div class="w-full h-64 md:h-80 bg-gray-200 rounded-lg mb-4">
             <img src="${item.images[0] ? apiBaseUrl + item.images[0] : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+"}"
                  alt="Hình ảnh sản phẩm" class="w-full h-full object-contain">
        </div>
        <h4 class="text-lg font-semibold">Mô tả</h4>
        <p class="text-gray-700 mt-1 whitespace-pre-wrap">${item.description || 'Không có mô tả.'}</p>
        ${productDetailsHtml}
    `;
}

/** Mở modal để tải ảnh lên. */
function uploadImage(id, listing_type) {
  const modal = document.getElementById('upload-modal');
  modal.classList.remove('hidden');
  modal.dataset.id = id;
  modal.dataset.type = listing_type;
  const fileInput = document.getElementById('upload-image-input');
  if (fileInput) fileInput.value = null;
}

/** Xác nhận và gửi ảnh lên server. */
async function confirmUpload() {
  const modal = document.getElementById('upload-modal');
  const fileInput = document.getElementById('upload-image-input');
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
    const listingsContainer = document.getElementById('listings-container');
    const auctionsContainer = document.getElementById('auctions-container');
    const listingTab = document.getElementById('listing-tab');
    const auctionTab = document.getElementById('auction-tab');

    if (!listingsContainer || !auctionsContainer || !listingTab || !auctionTab) return;

    if (tabName === 'listings') {
        listingsContainer.classList.remove('hidden');
        auctionsContainer.classList.add('hidden');
        listingTab.classList.add('border-indigo-500', 'text-indigo-600');
        listingTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
        auctionTab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
        auctionTab.classList.remove('border-indigo-500', 'text-indigo-600');
    } else if (tabName === 'auctions') {
        listingsContainer.classList.add('hidden');
        auctionsContainer.classList.remove('hidden');
        listingTab.classList.add('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
        listingTab.classList.remove('border-indigo-500', 'text-indigo-600');
        auctionTab.classList.add('border-indigo-500', 'text-indigo-600');
        auctionTab.classList.remove('border-transparent', 'text-gray-500', 'hover:text-gray-700', 'hover:border-gray-300');
    }
}

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  updateNav();
  const token = localStorage.getItem("jwt_token");

  if (token) {
    try {
      const payload = JSON.parse(atob(token.split(".")[1]));
      const currentTime = Math.floor(Date.now() / 1000);

      if (payload.exp && payload.exp < currentTime) {
        console.warn("Token has expired");
        localStorage.removeItem("jwt_token");
        navigateTo("home");
      } else {
        navigateTo("profile");
      }
    } catch (e) {
      console.error("Invalid token format", e);
      localStorage.removeItem("jwt_token");
      navigateTo("home");
    }
  } else {
    navigateTo("home");
  }
});


/** Hiển thị chi tiết một phiên đấu giá và form đặt giá. */
async function viewAuctionDetail(auctionId) {
    const modalContent = document.getElementById('detail-modal-content');
    document.getElementById('add-image-btn')?.remove();
    modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
    openModal('detail-modal');

    try {
        const item = await apiRequest(`/auction/api/${auctionId}`);
        if (item) {
            let productDetailsHtml = '';
            if (item.auction_type === 'vehicle' && item.vehicle_details) {
                productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Hãng xe:</strong> ${item.vehicle_details.brand || 'N/A'}</p>
                    <p><strong>Dòng xe:</strong> ${item.vehicle_details.model || 'N/A'}</p>
                    <p><strong>Năm sản xuất:</strong> ${item.vehicle_details.year || 'N/A'}</p>
                    <p><strong>Số KM đã đi:</strong> ${item.vehicle_details.mileage ? item.vehicle_details.mileage.toLocaleString() : 'N/A'}</p>
                    </div>`;
            } else if (item.auction_type === 'battery' && item.battery_details) {
                productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Nhà sản xuất:</strong> ${item.battery_details.manufacturer || 'N/A'}</p>
                    <p><strong>Dung lượng:</strong> ${item.battery_details.capacity_kwh ? item.battery_details.capacity_kwh + ' kWh' : 'N/A'}</p>
                    <p><strong>Tình trạng:</strong> ${item.battery_details.health_percent ? item.battery_details.health_percent + '%' : 'N/A'}</p>
                    </div>`;
            }

            modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${item.auction_id}</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(item.current_bid).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(item.start_time).toLocaleString('vi-VN')}</p>
                <p><strong>Kết thúc:</strong> ${new Date(item.end_time).toLocaleString('vi-VN')}</p>
                ${productDetailsHtml}
                
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Người bán</h4>
                <p>Người bán: ${item.seller_username ? `${item.seller_username} (ID: ${item.bidder_id})` : `ID: ${item.bidder_id}`}</p> 
                <p>Người thắng hiện tại: ${item.winner_username ? `${item.winner_username} (ID: ${item.winning_bidder_id})` : (item.winning_bidder_id ? `ID: ${item.winning_bidder_id}` : 'N/A')}</p>
                ${item.auction_status === 'started' ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${Number(item.current_bid) + 1}"
                           placeholder="Phải lớn hơn ${Number(item.current_bid).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                ` : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`}
            `;

            const bidForm = document.getElementById('bid-form');
            if (bidForm) {
                bidForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const bidAmount = document.getElementById('bid-amount').value;
                    try {
                        await apiRequest(`/auction/api/${auctionId}/bid`, 'POST', { bid_amount: parseFloat(bidAmount) });
                        showToast("Đặt giá thành công!");
                        closeModal('detail-modal');
                        loadPublicAuctions();
                    } catch (error) {}
                });
            }
        } else {
            modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
        }
    } catch (error) {
        modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
    }
}
async function loadPublicAuctions() {
    try {
        const auctions = await apiRequest("/auction/api/");
        const container = document.getElementById("auctions-container");

        if (auctions && Array.isArray(auctions) && auctions.length > 0) {
            container.innerHTML = auctions.map((item) => {
                let detailsHtml = "";
                if (item.auction_type === "vehicle" && item.vehicle_details) {
                    const v = item.vehicle_details;
                    detailsHtml = `<p class="text-gray-600">Xe: ${v.model || 'N/A'}</p>`;
                } else if (item.auction_type === "battery" && item.battery_details) {
                    const b = item.battery_details;
                    detailsHtml = `<p class="text-gray-600">Pin: ${b.name || 'N/A'}</p>`;
                }

                const startTime = new Date(item.start_time).toLocaleString('vi-VN');
                const endTime = new Date(item.end_time).toLocaleString('vi-VN');

                return `
                <div class="bg-white rounded-lg shadow-md overflow-hidden flex flex-col transition-transform transform hover:-translate-y-1">
                    <div class="p-4 flex flex-col flex-grow">
                        <h3 class="font-bold text-lg mb-2 truncate">Phiên đấu giá #${item.auction_id}</h3>
                        <span class="mb-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                            ${item.auction_status}
                        </span>
                        <div class="flex-grow mb-4">
                            ${detailsHtml}
                            <p class="text-sm text-gray-500">Bắt đầu: ${startTime}</p>
                            <p class="text-sm text-gray-500">Kết thúc: ${endTime}</p>
                        </div>
                        <div class="mt-auto flex justify-between items-center">
                            <div>
                                <p class="text-sm text-gray-500">Giá hiện tại:</p>
                                <p class="text-indigo-600 font-bold text-xl">${Number(item.current_bid).toLocaleString()} VNĐ</p>
                            </div>
                            <button onclick="viewAuctionDetail(${item.auction_id})" class="bg-indigo-500 text-white text-sm font-bold py-2 px-4 rounded hover:bg-indigo-600">Xem Chi Tiết</button>
                        </div>
                    </div>
                </div>
                `;
            }).join("");
        } else {
            container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-gray-600">Hiện chưa có phiên đấu giá nào.</p></div>`;
        }
    } catch (error) {
        const container = document.getElementById("auctions-container");
        container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách đấu giá.</p></div>`;
    }
}

async function viewBatteryAuctionDetail(battery_id) {
    const modalContent = document.getElementById('detail-modal-content');
    document.getElementById('add-image-btn')?.remove();
    modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
    openModal('detail-modal');

    try {
        const item = await apiRequest(`/auction/api/battery/${battery_id}`);
        if (item) {
            let productDetailsHtml = '';
            productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Nhà sản xuất:</strong> ${item.battery_details.manufacturer || 'N/A'}</p>
                    <p><strong>Dung lượng:</strong> ${item.battery_details.capacity_kwh ? item.battery_details.capacity_kwh + ' kWh' : 'N/A'}</p>
                    <p><strong>Tình trạng:</strong> ${item.battery_details.health_percent ? item.battery_details.health_percent + '%' : 'N/A'}</p>
                    </div>`;
            modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${item.auction_id}</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(item.current_bid).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(item.start_time).toLocaleString('vi-VN')}</p>
                <p><strong>Kết thúc:</strong> ${new Date(item.end_time).toLocaleString('vi-VN')}</p>
                ${productDetailsHtml}
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Thông tin đấu giá</h4>
                <p>Người bán: ${item.seller_username ? `${item.seller_username} (ID: ${item.bidder_id})` : `ID: ${item.bidder_id}`}</p> 
                <p>Người thắng hiện tại: ${item.winner_username ? `${item.winner_username} (ID: ${item.winning_bidder_id})` : (item.winning_bidder_id ? `ID: ${item.winning_bidder_id}` : 'N/A')}</p>
                ${item.auction_status === 'started' ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${Number(item.current_bid) + 1}"
                           placeholder="Phải lớn hơn ${Number(item.current_bid).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                ` : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`}
            `;
            const auctionId = item.auction_id

            const bidForm = document.getElementById('bid-form');
            if (bidForm) {
                bidForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const bidAmount = document.getElementById('bid-amount').value;
                    try {
                        await apiRequest(`/auction/api/${auctionId}/bid`, 'POST', { bid_amount: parseFloat(bidAmount) });
                        showToast("Đặt giá thành công!");
                        closeModal('detail-modal');
                        loadPublicAuctions();
                    } catch (error) {}
                });
            }
        } else {
            modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
        }
    } catch (error) {
        modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
    }
}

async function unauctionBattery(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ đấu giá pin này?")){
    try{
      await apiRequest(`/auction/api/auctions/batteries/${id}`, "DELETE");
      showToast("Gỡ đấu giá pin thành công.")
      loadMyBatteries()
    } catch(error){}
  }
}

async function viewVehicleAuctionDetail(vehicle_id) {
    const modalContent = document.getElementById('detail-modal-content');
    document.getElementById('add-image-btn')?.remove();
    modalContent.innerHTML = `<div class="animate-pulse h-64 bg-gray-200 rounded w-full"></div>`;
    openModal('detail-modal');

    try {
        const item = await apiRequest(`/auction/api/vehicle/${vehicle_id}`);
        if (item) {
            let productDetailsHtml = '';
            productDetailsHtml = `
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết xe</h4>
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                    <p><strong>Hãng xe:</strong> ${item.vehicle_details.brand || 'N/A'}</p>
                    <p><strong>Dòng xe:</strong> ${item.vehicle_details.model || 'N/A'}</p>
                    <p><strong>Năm sản xuất:</strong> ${item.vehicle_details.year || 'N/A'}</p>
                    <p><strong>Số KM đã đi:</strong> ${item.vehicle_details.mileage ? item.vehicle_details.mileage.toLocaleString() : 'N/A'}</p>
                    </div>`;
            modalContent.innerHTML = `
                <h3 class="text-2xl font-bold mb-2">Phiên đấu giá #${item.auction_id}</h3>
                <p class="text-xl font-bold text-indigo-600 mb-4">Giá hiện tại: ${Number(item.current_bid).toLocaleString()} VNĐ</p>
                <p><strong>Trạng thái:</strong> ${item.auction_status}</p>
                <p><strong>Bắt đầu:</strong> ${new Date(item.start_time).toLocaleString('vi-VN')}</p>
                <p><strong>Kết thúc:</strong> ${new Date(item.end_time).toLocaleString('vi-VN')}</p>
                ${productDetailsHtml}
                <h4 class="text-lg font-semibold mt-4 border-t pt-4">Người bán</h4>
                <p>Người bán: ${item.seller_username ? `${item.seller_username} (ID: ${item.bidder_id})` : `ID: ${item.bidder_id}`}</p> 
                <p>Người thắng hiện tại: ${item.winner_username ? `${item.winner_username} (ID: ${item.winning_bidder_id})` : (item.winning_bidder_id ? `ID: ${item.winning_bidder_id}` : 'N/A')}</p>
                ${item.auction_status === 'started' ? `
                <form id="bid-form" class="mt-6 border-t pt-4">
                    <label for="bid-amount" class="block text-sm font-medium text-gray-700">Giá đặt của bạn (VNĐ)</label>
                    <input type="number" id="bid-amount" min="${Number(item.current_bid) + 1}"
                           placeholder="Phải lớn hơn ${Number(item.current_bid).toLocaleString()}"
                           class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm" required>
                    <button type="submit" class="w-full mt-4 bg-green-600 text-white font-bold py-2 px-4 rounded-lg hover:bg-green-700">Đặt Giá</button>
                </form>
                ` : `<p class="mt-6 border-t pt-4 text-center font-semibold text-red-500">Phiên đấu giá chưa bắt đầu hoặc đã kết thúc.</p>`}
            `;
            const auctionId = item.auction_id

            const bidForm = document.getElementById('bid-form');
            if (bidForm) {
                bidForm.addEventListener('submit', async (e) => {
                    e.preventDefault();
                    const bidAmount = document.getElementById('bid-amount').value;
                    try {
                        await apiRequest(`/auction/api/${auctionId}/bid`, 'POST', { bid_amount: parseFloat(bidAmount) });
                        showToast("Đặt giá thành công!");
                        closeModal('detail-modal');
                        loadPublicAuctions();
                    } catch (error) {}
                });
            }
        } else {
            modalContent.innerHTML = '<p class="text-red-500">Không thể tải chi tiết đấu giá.</p>';
        }
    } catch (error) {
        modalContent.innerHTML = '<p class="text-red-500">Đã xảy ra lỗi khi tải dữ liệu.</p>';
    }
}


async function unauctionVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ đấu giá xe này?")){
    try{
      await apiRequest(`/auction/api/auctions/vehicles/${id}`, "DELETE");
      showToast("Gỡ đấu giá xe thành công.")
      loadMyVehicles()
    } catch(error){}
  }
}
