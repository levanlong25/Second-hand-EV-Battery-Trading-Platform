const apiBaseUrl = "http://localhost";

// --- DOM ELEMENTS ---
const navAuthLinks = document.getElementById("nav-auth-links");
const loadingSpinner = document.getElementById("loading-spinner");

// --- UTILS ---
const showLoading = () => loadingSpinner.classList.remove("hidden");
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
        }
    }
    
    modal.classList.add("active");
};
const closeModal = (modalId) =>
  document.getElementById(modalId).classList.remove("active");

// --- ROUTING ---
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
  if (pageId === "profile") {
    loadProfile();
    loadMyAssets();
  }
  if (pageId === "watchlist"){
    loadMyWatchlist();
  }
  if (pageId === "listings") {
    loadPublicListings();
  }
}

// --- AUTHENTICATION & API ---
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

function logout() {
  localStorage.removeItem("jwt_token");
  showToast("Bạn đã đăng xuất thành công.");
  updateNav();
  navigateTo("login");
}

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
    throw error; // Re-throw the error to be caught by the caller
  } finally {
    hideLoading();
  }
}
/**
 * Hiển thị hoặc ẩn form cập nhật thông tin cá nhân.
 * @param {boolean} [forceShow] - Nếu là true, form sẽ hiện ra. Nếu false, form sẽ ẩn đi.
 * Nếu để trống, hàm sẽ tự động đảo ngược trạng thái.
 */
function toggleProfileForm(forceShow) {
    const form = document.getElementById('profile-update-form');
    const buttonContainer = document.getElementById('update-profile-button-container');

    if (!form || !buttonContainer) return;

    const isHidden = form.classList.contains('hidden');

    if (forceShow === true) {
        // Bắt buộc hiện form
        form.classList.remove('hidden');
        buttonContainer.classList.add('hidden');
    } else if (forceShow === false) {
        // Bắt buộc ẩn form
        form.classList.add('hidden');
        buttonContainer.classList.remove('hidden');
    } else {
        // Tự động đảo ngược
        form.classList.toggle('hidden');
        buttonContainer.classList.toggle('hidden');
    }
}

// Hàm loadProfile của bạn giữ nguyên, nó đã hoạt động đúng.
async function loadProfile() {
  try {
    const data = await apiRequest("/user/api/profile");
    if (data) {
      // Hiển thị thông tin
      const detailsDiv = document.getElementById("profile-details");
      detailsDiv.innerHTML = `
                      <p><strong>Họ và tên:</strong> ${
                        data.full_name || "Chưa cập nhật"
                      }</p>
                      <p><strong>Điện thoại:</strong> ${
                        data.phone_number || "Chưa cập nhật"
                      }</p>
                      <p><strong>Địa chỉ:</strong> ${
                        data.address || "Chưa cập nhật"
                      }</p>
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
async function loadMyAssets() {
  loadMyVehicles();
  loadMyBatteries();
}

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

function openListingModal(type, id) {
  openModal("listing-modal", { type, id });
}

// --- EVENT LISTENERS ---
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
    }
    else { showToast("Đăng nhập thất bại. Vui lòng thử lại.", true); }
  } catch (error) {

  }
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

// Xử lý form gửi email để nhận OTP
document.getElementById("forget-password-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forget-email").value;
    try {
        const data = await apiRequest("/user/api/send-otp", "POST", { email });
        if (data) {
            showToast(data.message || "OTP đã được gửi đến email của bạn.");
            // Ẩn form gửi email và hiện form đặt lại mật khẩu
            document.getElementById("forget-password-form").classList.add("hidden");
            document.getElementById("reset-password-form").classList.remove("hidden");
        }
    } catch (error) {}
});
 
// Xử lý form đặt lại mật khẩu bằng OTP
document.getElementById("reset-password-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const email = document.getElementById("forget-email").value; // Lấy lại email đã nhập
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
            navigateTo("login"); // Chuyển về trang đăng nhập
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

// --- INITIALIZATION ---
document.addEventListener("DOMContentLoaded", () => {
  updateNav();
  const token = localStorage.getItem("jwt_token");

  if (token) {
    try {
      // Giải mã phần payload của JWT (phần ở giữa)
      const payload = JSON.parse(atob(token.split(".")[1]));
      const currentTime = Math.floor(Date.now() / 1000); // giây hiện tại

      // Nếu token hết hạn
      if (payload.exp && payload.exp < currentTime) {
        console.warn("Token has expired");
        localStorage.removeItem("jwt_token"); // xóa token cũ
        navigateTo("home"); // quay về trang home
      } else {
        navigateTo("profile"); // token còn hạn → vào profile
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
      console.error("❌ Invalid JSON response:", responseText);
      responseData = { message: responseText || "Operation successful" };
    }
  });


async function loadPublicListings() {
  try {
    // Gọi API công khai để lấy các tin đăng đã được duyệt
    const listings = await apiRequest("/listing/api/listings");
    const container = document.getElementById("listings-container");

    if (listings && Array.isArray(listings) && listings.length > 0) {
      container.innerHTML = listings
        .map((item) => {
          let detailsHtml = "";
          // Xử lý hiển thị chi tiết cho xe
          if (item.listing_type === "vehicle" && item.vehicle_details) {
            const v = item.vehicle_details;
            detailsHtml = `
                                <p class="text-gray-600">Hãng xe: ${
                                  v.brand
                                } | Dòng xe: ${v.model} | Năm sản xuất: ${
              v.year
            }</p>
                                <p class="text-sm text-gray-500">Số KM: ${v.mileage.toLocaleString()}</p>
                            `;
          }
          // Xử lý hiển thị chi tiết cho pin
          else if (item.listing_type === "battery" && item.battery_details) {
            const b = item.battery_details;
            detailsHtml = `
                                <p class="text-gray-600">Nhà sản xuất: ${b.manufacturer}</p>
                                <p class="text-sm text-gray-500">${b.capacity_kwh}kWh | Tình trạng: ${b.health_percent}%</p>
                            `;
          }

          // Template HTML cho mỗi thẻ sản phẩm
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
        })
        .join("");
    } else {
      // Hiển thị thông báo nếu không có tin đăng nào
      container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-gray-600">Hiện chưa có tin đăng nào.</p></div>`;
    }
  } catch (error) {
    // Nếu API lỗi, hiển thị thông báo trong container
    const container = document.getElementById("listings-container");
    container.innerHTML = `<div class="col-span-full bg-white p-6 rounded-lg shadow text-center"><p class="text-red-500">Không thể tải danh sách tin đăng. Vui lòng thử lại.</p></div>`;
  }
}

async function viewDetail(listingId) {  
    const modalContent = document.getElementById('detail-modal-content'); 
    modalContent.innerHTML = `
        <div class="animate-pulse">
            <div class="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div class="h-64 bg-gray-200 rounded w-full mb-4"></div>
            <div class="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>`;
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
            </div>
        `;
    } 
    // Tạo HTML cho chi tiết pin
    else if (item.listing_type === 'battery' && item.battery_details) {
        const b = item.battery_details;
        productDetailsHtml = `
            <h4 class="text-lg font-semibold mt-4 border-t pt-4">Chi tiết pin</h4>
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 text-sm mt-2">
                <p><strong>Nhà sản xuất:</strong> ${b.manufacturer}</p>
                <p><strong>Dung lượng:</strong> ${b.capacity_kwh} kWh</p>
                <p><strong>Tình trạng:</strong> ${b.health_percent}%</p>
            </div>
        `;
    }
 
    const detailHtml = `
        <h3 class="text-2xl font-bold mb-2">${item.title}</h3>
        <p class="text-2xl font-bold text-indigo-600 mb-4">${Number(item.price).toLocaleString()} VNĐ</p>
        <div class="w-full h-64 md:h-80 bg-gray-200 rounded-lg mb-4">
             <img src="${
                    item.images[0] 
                    ? apiBaseUrl + item.images[0] 
                    : "https://placehold.co/600x400/e2e8f0/e2e8f0?text=+"
                }" alt="..." class="w-full h-full object-contain"> 
        </div>
        <h4 class="text-lg font-semibold">Mô tả</h4>
        <p class="text-gray-700 mt-1 whitespace-pre-wrap">${item.description || 'Không có mô tả.'}</p>
        ${productDetailsHtml}
    `;
    
    modalContent.innerHTML = detailHtml;
}

function uploadImage(id, listing_type) {
  const modal = document.getElementById('upload-modal');
  modal.classList.remove('hidden'); 
  modal.dataset.id = '';
  modal.dataset.type = '';

  modal.dataset.id = id;
  modal.dataset.type = listing_type; 
  const fileInput = document.getElementById('upload-image-input');
  if (fileInput) fileInput.value = null;
}


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
    alert("Tải ảnh thành công!");

  } catch (err) {
    console.error("Upload error:", err);
    alert("Lỗi khi tải ảnh lên!");
  } finally { 
    fileInput.value = null;
  }
}

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

async function deleteBattery(id) {
  if (confirm("Bạn có chắc chắn muốn xóa pin này khỏi kho?")) {
    try {
      await apiRequest(`/listing/api/my-assets/batteries/${id}`, "DELETE");
      showToast("Xóa pin thành công.");
      loadMyBatteries();
    } catch (error) {}
  }
}

async function unlistBattery(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ bán pin này?")) {
    try {
      await apiRequest(`/listing/api/my-assets/batteries/${id}/list`, "DELETE");
      showToast("Gỡ bán pin thành công.");
      loadMyBatteries();
    } catch (error) {}
  }
}
 

// Biến toàn cục để lưu trữ danh sách pin sau khi gọi API
let allMyBatteries = [];

/**
 * Hàm render danh sách pin ra container.
 * @param {boolean} showAll - Nếu true, hiển thị tất cả pin. Nếu false, chỉ hiển thị 2 pin đầu tiên.
 */
function renderMyBatteries(showAll = false) {
    const container = document.getElementById("my-batteries-container");
    if (!container) return;

    // Xử lý trường hợp không có pin
    if (!allMyBatteries || allMyBatteries.length === 0) {
        container.innerHTML = `<p class="text-gray-500">Bạn chưa có pin nào trong kho.</p>`;
        return;
    }

    // Xác định danh sách pin cần hiển thị
    const batteriesToDisplay = showAll ? allMyBatteries : allMyBatteries.slice(0, 2);

    // Tạo HTML cho các mục pin
    let contentHTML = batteriesToDisplay.map(b => `
        <div class="border rounded-lg p-4 flex justify-between items-center bg-white">
            <div>
                <p class="font-bold flex items-center">
                    Nhà sản xuất: ${b.manufacturer}
                    ${b.is_listed ? renderStatusBadge(b.battery_id) : ""}
                </p>
                <p class="text-sm text-gray-600">
                    ${
                      b.is_listed
                        ? `<button onclick="viewBatteryDetail('${b.battery_id}')" class="bg-indigo-000 text-gray-400 text-[0.6rem] rounded hover:bg-indigo-100">Xem Chi Tiết</button>`
                        : `<p class="text-sm text-gray-600">Dung lượng: ${b.capacity_kwh} | kWh - Tình trạng: ${b.health_percent}%</p>`
                    }
                </p>
            </div>
            <div class="space-x-2">
                ${
                  b.is_listed
                    ? `<button onclick="unlistBattery(${b.battery_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`
                    : `<button onclick="openListingModal('battery', ${b.battery_id})" class="bg-blue-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-blue-600">Đăng Bán</button>`
                }
                <button onclick='openModal("battery-modal", ${JSON.stringify(b)})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
                <button onclick="deleteBattery(${b.battery_id})" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button> 
            </div>
        </div>
    `).join("");

    // Thêm nút "Hiển thị toàn bộ" hoặc "Ẩn bớt" nếu cần
    if (allMyBatteries.length > 2) {
        if (showAll) {
            contentHTML += `
                <div class="text-center mt-4">
                    <button onclick="renderMyBatteries(false)" class="text-blue-600 hover:underline font-semibold">Ẩn bớt</button>
                </div>`;
        } else {
            contentHTML += `
                <div class="text-center mt-4">
                    <button onclick="renderMyBatteries(true)" class="text-blue-600 hover:underline font-semibold">Hiển thị toàn bộ (${allMyBatteries.length})</button>
                </div>`;
        }
    }

    container.innerHTML = contentHTML;
} 
async function loadMyBatteries() {
    try {
        const batteries = await apiRequest("/listing/api/my-assets/batteries");
        // Lưu dữ liệu vào biến toàn cục
        allMyBatteries = (batteries && Array.isArray(batteries)) ? batteries : [];
        // Gọi hàm render lần đầu (chỉ hiển thị 2 mục)
        renderMyBatteries(); 
    } catch (error) {
        console.error("Failed to load batteries:", error);
        allMyBatteries = []; // Đảm bảo mảng rỗng nếu có lỗi
        renderMyBatteries(); // Hiển thị thông báo lỗi hoặc không có pin
    }
}

async function viewBatteryDetail(battery_id) {  
    const modalContent = document.getElementById('detail-modal-content'); 
    modalContent.innerHTML = `
        <div class="animate-pulse">
            <div class="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div class="h-64 bg-gray-200 rounded w-full mb-4"></div>
            <div class="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div class="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>`; 
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


async function deleteVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn xóa xe này khỏi kho?")) {
    try {
      await apiRequest(`/listing/api/my-assets/vehicles/${id}`, "DELETE");
      showToast("Xóa xe thành công.");
      loadMyVehicles();
    } catch (error) {}
  }
}


async function unlistVehicle(id) {
  if (confirm("Bạn có chắc chắn muốn gỡ bán xe này?")) {
    try {
      await apiRequest(`/listing/api/my-assets/vehicles/${id}/list`, "DELETE");
      showToast("Gỡ bán xe thành công.");
      loadMyVehicles();
    } catch (error) {}
  }
}


let allMyVehicles = [];

/**
 * Hàm render danh sách xe ra container.
 * @param {boolean} showAll - Nếu true, hiển thị tất cả xe. Nếu false, chỉ hiển thị 2 xe đầu tiên.
 */
function renderMyVehicles(showAll = false) {
    const container = document.getElementById("my-vehicles-container");
    if (!container) return;

    // Xử lý trường hợp không có xe
    if (!allMyVehicles || allMyVehicles.length === 0) {
        container.innerHTML = `<p class="text-gray-500">Bạn chưa có xe nào trong kho.</p>`;
        return;
    }

    // Xác định danh sách xe cần hiển thị
    const vehiclesToDisplay = showAll ? allMyVehicles : allMyVehicles.slice(0, 2);

    // Tạo HTML cho các mục xe
    let contentHTML = vehiclesToDisplay.map(v => `
        <div class="border rounded-lg p-4 flex justify-between items-center bg-white">
            <div>
                <p class="font-bold flex items-center">
                    Hãng xe: ${v.brand} (${v.year})
                    ${v.is_listed ? renderStatusBadge(v.listing_status) : ""}
                </p>
                <p class="text-sm text-gray-600">
                    ${
                      v.is_listed
                        ? `<button onclick="viewVehicleDetail('${v.vehicle_id}')" class="bg-indigo-000 text-gray-400 text-[0.6rem] rounded hover:bg-indigo-100">Xem Chi Tiết</button>`
                        : `<p class="text-sm text-gray-600">Dòng xe: ${v.model} | Số KM: ${v.mileage.toLocaleString()}</p>`
                    }
                </p>
            </div>
            <div class="space-x-2">
                ${
                  v.is_listed
                    ? `<button onclick="unlistVehicle(${v.vehicle_id})" class="bg-yellow-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-yellow-600">Gỡ Bán</button>`
                    : `<button onclick="openListingModal('vehicle', ${v.vehicle_id})" class="bg-blue-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-blue-600">Đăng Bán</button>`
                }
                <button onclick='openModal("vehicle-modal", ${JSON.stringify(v)})' class="bg-gray-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-gray-600">Sửa</button>
                <button onclick="deleteVehicle(${v.vehicle_id})" class="bg-red-500 text-white text-sm font-bold py-1 px-3 rounded hover:bg-red-600">Xóa</button>
            </div>
        </div>
    `).join("");

    // Thêm nút "Hiển thị toàn bộ" hoặc "Ẩn bớt" nếu cần
    if (allMyVehicles.length > 2) {
        if (showAll) {
            contentHTML += `
                <div class="text-center mt-4">
                    <button onclick="renderMyVehicles(false)" class="text-blue-600 hover:underline font-semibold">Ẩn bớt</button>
                </div>`;
        } else {
            contentHTML += `
                <div class="text-center mt-4">
                    <button onclick="renderMyVehicles(true)" class="text-blue-600 hover:underline font-semibold">Hiển thị toàn bộ (${allMyVehicles.length})</button>
                </div>`;
        }
    }

    container.innerHTML = contentHTML;
} 
async function loadMyVehicles() {
    try {
        const vehicles = await apiRequest("/listing/api/my-assets/vehicles");
        // Lưu dữ liệu vào biến toàn cục
        allMyVehicles = (vehicles && Array.isArray(vehicles)) ? vehicles : [];
        // Gọi hàm render lần đầu (chỉ hiển thị 2 mục)
        renderMyVehicles(); 
    } catch (error) {
        console.error("Failed to load vehicles:", error);
        allMyVehicles = []; // Đảm bảo mảng rỗng nếu có lỗi
        renderMyVehicles(); // Hiển thị thông báo lỗi hoặc không có xe
    }
}

async function viewVehicleDetail(vehicle_id) {  
  const modalContent = document.getElementById('detail-modal-content'); 
  modalContent.innerHTML = `
    <div class="animate-pulse">
      <div class="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div class="h-64 bg-gray-200 rounded w-full mb-4"></div>
      <div class="h-4 bg-gray-200 rounded w-full mb-2"></div>            
      <div class="h-4 bg-gray-200 rounded w-1/2"></div>
    </div>`;
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

