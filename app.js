/* ========================================
   CampusLost - College Lost & Found Portal
   JavaScript Application (Flask Backend)
   ======================================== */

// API Base URL
const API_URL = 'http://localhost:5000/api';

// ========================================
// State Management
// ========================================

let currentUser = null;
let currentPage = 'home';
let reportType = 'lost';
let uploadedImage = null;

// Initialize app
function init() {
    loadCurrentUser();
    setupEventListeners();
    updateUI();
    navigateTo('home');
}

// ========================================
// API Helper Functions
// ========================================

async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('campusLost_token');
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// ========================================
// User Authentication
// ========================================

function loadCurrentUser() {
    const user = localStorage.getItem('campusLost_user');
    if (user && user !== 'null') {
        currentUser = JSON.parse(user);
    }
}

function saveCurrentUser(user, token) {
    currentUser = user;
    localStorage.setItem('campusLost_user', JSON.stringify(user));
    localStorage.setItem('campusLost_token', token);
}

async function handleLogin(event) {
    event.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const result = await apiCall('/login', 'POST', { email, password });
        
        saveCurrentUser(result.user, result.token);
        closeAuthModal();
        updateUI();
        showToast('success', 'Welcome back!', `Logged in as ${result.user.name}`);
        navigateTo('home');
    } catch (error) {
        showToast('error', 'Login Failed', error.message);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const name = document.getElementById('regName').value;
    const email = document.getElementById('regEmail').value;
    const phone = document.getElementById('regPhone').value;
    const password = document.getElementById('regPassword').value;
    const confirmPassword = document.getElementById('regConfirmPassword').value;
    
    if (password !== confirmPassword) {
        showToast('error', 'Registration Failed', 'Passwords do not match');
        return;
    }
    
    try {
        const result = await apiCall('/register', 'POST', { name, email, phone, password });
        
        saveCurrentUser(result.user, result.token);
        closeAuthModal();
        updateUI();
        showToast('success', 'Welcome!', 'Account created successfully');
        navigateTo('home');
    } catch (error) {
        showToast('error', 'Registration Failed', error.message);
    }
}

function logout() {
    currentUser = null;
    localStorage.removeItem('campusLost_user');
    localStorage.removeItem('campusLost_token');
    updateUI();
    navigateTo('home');
    showToast('info', 'Logged Out', 'You have been logged out');
}

// ========================================
// Navigation
// ========================================

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    
    const pageElement = document.getElementById(page + 'Page');
    if (pageElement) {
        pageElement.classList.add('active');
    }
    
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
        if (link.dataset.page === page) {
            link.classList.add('active');
        }
    });
    
    currentPage = page;
    
    switch (page) {
        case 'home':
            loadHomePage();
            break;
        case 'lost':
            loadLostItems();
            break;
        case 'found':
            loadFoundItems();
            break;
        case 'myitems':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to view your items');
                openAuthModal();
                return;
            }
            loadMyItems();
            break;
        case 'report':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to report an item');
                openAuthModal();
                return;
            }
            resetReportForm();
            break;
        case 'dashboard':
            if (!currentUser) {
                showToast('error', 'Login Required', 'Please login to view dashboard');
                openAuthModal();
                return;
            }
            loadDashboard();
            break;
        case 'admin':
            if (!currentUser || currentUser.role !== 'admin') {
                showToast('error', 'Access Denied', 'Admin access required');
                navigateTo('home');
                return;
            }
            loadAdminDashboard();
            break;
    }
    
    window.scrollTo(0, 0);
}

// ========================================
// UI Components
// ========================================

function updateUI() {
    const userSection = document.getElementById('userSection');
    const userDropdown = document.getElementById('userDropdown');
    const adminLink = document.getElementById('adminLink');
    
    if (currentUser) {
        userSection.classList.add('hidden');
        userDropdown.classList.remove('hidden');
        
        document.getElementById('userAvatar').textContent = currentUser.name.charAt(0).toUpperCase();
        document.getElementById('userName').textContent = currentUser.name;
        document.getElementById('userEmail').textContent = currentUser.email;
        
        if (currentUser.role === 'admin') {
            adminLink.style.display = 'flex';
        } else {
            adminLink.style.display = 'none';
        }
    } else {
        userSection.classList.remove('hidden');
        userDropdown.classList.add('hidden');
    }
    
    updateNotificationBadge();
    updateStats();
}

function toggleMobileMenu() {
    const nav = document.getElementById('mainNav');
    nav.classList.toggle('show');
}

function toggleUserMenu() {
    const menu = document.getElementById('dropdownMenu');
    menu.classList.toggle('show');
}

async function toggleNotifications() {
    const panel = document.getElementById('notificationPanel');
    panel.classList.toggle('hidden');
    if (!panel.classList.contains('hidden')) {
        await loadNotifications();
    }
}

// ========================================
// Auth Modal
// ========================================

function openAuthModal(tab = 'login') {
    const modal = document.getElementById('authModal');
    modal.classList.remove('hidden');
    switchAuthTab(tab);
}

function closeAuthModal() {
    const modal = document.getElementById('authModal');
    modal.classList.add('hidden');
    document.getElementById('loginForm').reset();
    document.getElementById('registerForm').reset();
}

function switchAuthTab(tab) {
    const tabs = document.querySelectorAll('.auth-tab');
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tab) {
            t.classList.add('active');
        }
    });
    
    if (tab === 'login') {
        loginForm.classList.remove('hidden');
        registerForm.classList.add('hidden');
    } else {
        loginForm.classList.add('hidden');
        registerForm.classList.remove('hidden');
    }
}

// ========================================
// Item Modal
// ========================================

async function openItemModal(itemId) {
    try {
        const item = await apiCall(`/items/${itemId}`);
        
        const modal = document.getElementById('itemDetailModal');
        const content = document.getElementById('itemDetailContent');
        
        const icon = getCategoryIcon(item.category);
        const typeLabel = item.type === 'lost' ? 'Lost' : 'Found';
        const statusClass = item.status === 'resolved' || item.status === 'claimed' ? 'resolved' : item.status;
        
        content.innerHTML = `
            <div class="item-detail-image">${icon}</div>
            <span class="item-badge ${item.type}">${typeLabel}</span>
            <span class="item-badge ${statusClass}">${item.status}</span>
            <h2>${item.name}</h2>
            <div class="item-detail-meta">
                <span class="item-category">${capitalize(item.category)}</span>
            </div>
            
            <div class="item-detail-description">
                <h4>Description</h4>
                <p>${item.description}</p>
            </div>
            
            <div class="item-detail-info">
                <div class="info-item">
                    <div class="info-label">${item.type === 'lost' ? 'Last Seen' : 'Found'} Location</div>
                    <div class="info-value">${item.location}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">${item.type === 'lost' ? 'Last Seen' : 'Found'} Date</div>
                    <div class="info-value">${formatDate(item.date)}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Posted By</div>
                    <div class="info-value">${item.user_name}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Posted On</div>
                    <div class="info-value">${formatDate(item.created_at)}</div>
                </div>
            </div>
            
            <div class="item-detail-actions">
                ${currentUser && currentUser.id !== item.user_id ? `
                    <button class="btn btn-primary" onclick="contactOwner(${item.id})">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        Contact ${item.type === 'lost' ? 'Owner' : 'Finder'}
                    </button>
                    ${item.type === 'found' ? `
                        <button class="btn btn-secondary" onclick="openClaimModal(${item.id})">
                            This is Mine
                        </button>
                    ` : ''}
                ` : ''}
                ${currentUser && currentUser.id === item.user_id ? `
                    <button class="btn btn-secondary" onclick="deleteItem(${item.id})">
                        Delete
                    </button>
                ` : ''}
            </div>
        `;
        
        modal.classList.remove('hidden');
    } catch (error) {
        showToast('error', 'Error', 'Failed to load item details');
    }
}

function closeItemModal() {
    const modal = document.getElementById('itemDetailModal');
    modal.classList.add('hidden');
}

// ========================================
// Claim Modal
// ========================================

function openClaimModal(itemId) {
    closeItemModal();
    const modal = document.getElementById('claimModal');
    document.getElementById('claimItemId').value = itemId;
    modal.classList.remove('hidden');
}

function closeClaimModal() {
    const modal = document.getElementById('claimModal');
    modal.classList.add('hidden');
    document.getElementById('claimForm').reset();
}

async function submitClaim(event) {
    event.preventDefault();
    
    if (!currentUser) {
        showToast('error', 'Login Required', 'Please login to submit a claim');
        openAuthModal();
        return;
    }
    
    const itemId = parseInt(document.getElementById('claimItemId').value);
    const proof = document.getElementById('claimProof').value;
    const contact = document.getElementById('claimContact').value;
    
    try {
        await apiCall('/claims', 'POST', { item_id: itemId, proof, contact });
        
        closeClaimModal();
        showToast('success', 'Claim Submitted', 'Your claim is pending approval');
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

// ========================================
// Home Page
// ========================================

async function loadHomePage() {
    try {
        const items = await apiCall('/items');
        
        const recentItems = items.slice(0, 6);
        const grid = document.getElementById('recentItemsGrid');
        grid.innerHTML = recentItems.map(item => createItemCard(item)).join('');
        
        updateStats();
    } catch (error) {
        console.error('Error loading home:', error);
    }
}

async function updateStats() {
    try {
        if (currentUser && currentUser.role === 'admin') {
            const stats = await apiCall('/admin/stats');
            document.getElementById('adminUserCount').textContent = stats.total_users;
            document.getElementById('adminLostCount').textContent = stats.lost_items;
            document.getElementById('adminFoundCount').textContent = stats.found_items;
            document.getElementById('adminPendingCount').textContent = stats.pending_claims;
        }
        
        const items = await apiCall('/items');
        const lostItems = items.filter(i => i.type === 'lost').length;
        const foundItems = items.filter(i => i.type === 'found').length;
        const resolved = items.filter(i => i.status === 'resolved' || i.status === 'claimed').length;
        
        document.getElementById('totalLostItems').textContent = lostItems;
        document.getElementById('totalFoundItems').textContent = foundItems;
        document.getElementById('totalReunited').textContent = resolved;
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

async function switchRecentTab(tab) {
    const tabs = document.querySelectorAll('#homePage .section-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
        if (t.dataset.tab === tab) {
            t.classList.add('active');
        }
    });
    
    try {
        let items;
        if (tab === 'recent') {
            items = await apiCall('/items');
        } else {
            items = await apiCall(`/items?type=${tab}`);
        }
        
        const recentItems = items.slice(0, 6);
        const grid = document.getElementById('recentItemsGrid');
        grid.innerHTML = recentItems.map(item => createItemCard(item)).join('');
        
        if (recentItems.length === 0) {
            grid.innerHTML = `<div class="empty-state">No ${tab === 'recent' ? '' : tab + ' '}items found</div>`;
        }
    } catch (error) {
        console.error('Error switching tab:', error);
    }
}

// ========================================
// Lost Items Page
// ========================================

async function loadLostItems() {
    await filterItems('lost');
}

async function filterItems(type) {
    const searchInput = document.getElementById(type + 'SearchInput');
    const categoryFilter = document.getElementById(type + 'CategoryFilter');
    const sortFilter = document.getElementById(type + 'SortFilter');
    
    const search = searchInput ? searchInput.value : '';
    const category = categoryFilter ? categoryFilter.value : '';
    const sort = sortFilter ? sortFilter.value : 'newest';
    
    let url = `/items?type=${type}`;
    if (search) url += `&search=${encodeURIComponent(search)}`;
    if (category) url += `&category=${category}`;
    
    try {
        let items = await apiCall(url);
        
        // Sort
        items.sort((a, b) => {
            const dateA = new Date(a.created_at);
            const dateB = new Date(b.created_at);
            return sort === 'newest' ? dateB - dateA : dateA - dateB;
        });
        
        const grid = document.getElementById(type + 'ItemsGrid');
        grid.innerHTML = items.map(item => createItemCard(item)).join('');
        
        if (items.length === 0) {
            grid.innerHTML = `<div class="empty-state">No ${type} items found</div>`;
        }
    } catch (error) {
        console.error('Error filtering items:', error);
    }
}

function loadMoreItems(type) {
    showToast('info', 'Loaded', 'All items loaded');
}

// ========================================
// Found Items Page
// ========================================

async function loadFoundItems() {
    await filterItems('found');
}

// ========================================
// Report Item
// ========================================

function selectReportType(type) {
    reportType = type;
    const buttons = document.querySelectorAll('.type-btn');
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.type === type) {
            btn.classList.add('active');
        }
    });
}

function resetReportForm() {
    document.getElementById('reportForm').reset();
    uploadedImage = null;
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('imageUpload').classList.remove('hidden');
    document.getElementById('itemDate').valueAsDate = new Date();
}

function previewImage(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            uploadedImage = e.target.result;
            document.getElementById('previewImg').src = uploadedImage;
            document.getElementById('imageUpload').classList.add('hidden');
            document.getElementById('imagePreview').classList.remove('hidden');
        };
        reader.readAsDataURL(file);
    }
}

function removeImage() {
    uploadedImage = null;
    document.getElementById('itemImage').value = '';
    document.getElementById('imagePreview').classList.add('hidden');
    document.getElementById('imageUpload').classList.remove('hidden');
}

async function submitReport(event) {
    event.preventDefault();
    
    if (!currentUser) {
        showToast('error', 'Login Required', 'Please login to report an item');
        openAuthModal();
        return;
    }
    
    const name = document.getElementById('itemName').value;
    const category = document.getElementById('itemCategory').value;
    const description = document.getElementById('itemDescription').value;
    const location = document.getElementById('itemLocation').value;
    const date = document.getElementById('itemDate').value;
    
    try {
        await apiCall('/items', 'POST', {
            type: reportType,
            name,
            category,
            description,
            location,
            date,
            image: uploadedImage
        });
        
        resetReportForm();
        showToast('success', 'Item Reported', `Your ${reportType} item has been posted successfully`);
        navigateTo(reportType === 'lost' ? 'lost' : 'found');
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

// ========================================
// My Items Page
// ========================================

async function loadMyItems() {
    if (!currentUser) return;
    switchMyItemsTab('lost');
}

async function switchMyItemsTab(tab) {
    const tabs = document.querySelectorAll('#myitemsPage .myitems-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
    });
    
    // Find the correct tab button
    const tabButtons = document.querySelectorAll('#myitemsPage .myitems-tabs .tab-btn');
    if (tab === 'lost') tabButtons[0].classList.add('active');
    else if (tab === 'found') tabButtons[1].classList.add('active');
    else if (tab === 'claims') tabButtons[2].classList.add('active');
    
    const content = document.getElementById('myitemsContent');
    
    if (tab === 'lost' || tab === 'found') {
        try {
            const items = await apiCall(`/my-items?type=${tab}`);
            
            if (items.length === 0) {
                content.innerHTML = `<div class="empty-state">No ${tab} items found</div>`;
            } else {
                content.innerHTML = `<div class="items-grid">${items.map(item => createItemCard(item)).join('')}</div>`;
            }
        } catch (error) {
            console.error('Error loading items:', error);
        }
    } else if (tab === 'claims') {
        try {
            const claims = await apiCall('/my-claims');
            
            if (claims.length === 0) {
                content.innerHTML = `<div class="empty-state">No claims found</div>`;
            } else {
                content.innerHTML = `
                    <div class="admin-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Item</th>
                                    <th>Type</th>
                                    <th>Date</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${claims.map(claim => `
                                    <tr>
                                        <td>${claim.item_name}</td>
                                        <td><span class="item-badge ${claim.item_type}">${capitalize(claim.item_type)}</span></td>
                                        <td>${formatDate(claim.created_at)}</td>
                                        <td><span class="status-badge ${claim.status}">${capitalize(claim.status)}</span></td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error loading claims:', error);
        }
    }
}

// ========================================
// Dashboard
// ========================================

async function loadDashboard() {
    if (!currentUser) return;
    
    document.getElementById('dashboardUserName').textContent = currentUser.name;
    
    try {
        const items = await apiCall('/my-items');
        const claims = await apiCall('/my-claims');
        
        const myLost = items.filter(i => i.type === 'lost').length;
        const myFound = items.filter(i => i.type === 'found').length;
        const myClaims = claims.filter(c => c.status === 'pending').length;
        const resolved = items.filter(i => i.status === 'resolved' || i.status === 'claimed').length;
        
        document.getElementById('myLostCount').textContent = myLost;
        document.getElementById('myFoundCount').textContent = myFound;
        document.getElementById('myClaimsCount').textContent = myClaims;
        document.getElementById('myResolvedCount').textContent = resolved;
        
        // Load recent activity
        const activityList = document.getElementById('activityList');
        
        if (items.length === 0) {
            activityList.innerHTML = '<div class="empty-state">No recent activity</div>';
        } else {
            const recentItems = items.slice(0, 5);
            activityList.innerHTML = recentItems.map(item => `
                <div class="activity-item">
                    <div class="activity-icon">${item.type === 'lost' ? '🔍' : '✨'}</div>
                    <div class="activity-content">
                        <div class="activity-text">You reported a ${item.type} item: ${item.name}</div>
                        <div class="activity-time">${formatDate(item.created_at)}</div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ========================================
// Admin Dashboard
// ========================================

let adminTab = 'items';

async function loadAdminDashboard() {
    try {
        const stats = await apiCall('/admin/stats');
        
        document.getElementById('adminUserCount').textContent = stats.total_users;
        document.getElementById('adminLostCount').textContent = stats.lost_items;
        document.getElementById('adminFoundCount').textContent = stats.found_items;
        document.getElementById('adminPendingCount').textContent = stats.pending_claims;
        
        switchAdminTab(adminTab);
    } catch (error) {
        console.error('Error loading admin:', error);
    }
}

async function switchAdminTab(tab) {
    adminTab = tab;
    const tabs = document.querySelectorAll('#adminPage .admin-tabs .tab-btn');
    tabs.forEach(t => {
        t.classList.remove('active');
    });
    
    // Find the correct tab
    const tabButtons = document.querySelectorAll('#adminPage .admin-tabs .tab-btn');
    if (tab === 'items') tabButtons[0].classList.add('active');
    else if (tab === 'users') tabButtons[1].classList.add('active');
    else if (tab === 'claims') tabButtons[2].classList.add('active');
    
    const content = document.getElementById('adminContent');
    
    try {
        if (tab === 'items') {
            const items = await apiCall('/items');
            
            content.innerHTML = `
                <div class="admin-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Type</th>
                                <th>Category</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${items.map(item => `
                                <tr>
                                    <td>${item.name}</td>
                                    <td><span class="item-badge ${item.type}">${capitalize(item.type)}</span></td>
                                    <td>${capitalize(item.category)}</td>
                                    <td><span class="status-badge ${item.status}">${capitalize(item.status)}</span></td>
                                    <td class="action-buttons">
                                        <button class="approve" onclick="adminResolveItem(${item.id})">Resolve</button>
                                        <button class="delete" onclick="adminDeleteItem(${item.id})">Delete</button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        } else if (tab === 'users') {
            // For now, show simplified user view
            content.innerHTML = `<div class="empty-state">User management coming soon</div>`;
        } else if (tab === 'claims') {
            const claims = await apiCall('/admin/claims');
            
            content.innerHTML = `
                <div class="admin-table">
                    <table>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Claimant</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${claims.map(claim => `
                                <tr>
                                    <td>${claim.item_name}</td>
                                    <td>${claim.claimant_name}</td>
                                    <td><span class="status-badge ${claim.status}">${capitalize(claim.status)}</span></td>
                                    <td class="action-buttons">
                                        ${claim.status === 'pending' ? `
                                            <button class="approve" onclick="adminApproveClaim(${claim.id})">Approve</button>
                                            <button class="reject" onclick="adminRejectClaim(${claim.id})">Reject</button>
                                        ` : ''}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error switching admin tab:', error);
    }
}

async function adminResolveItem(itemId) {
    try {
        await apiCall(`/items/${itemId}`, 'PUT', { status: 'resolved' });
        showToast('success', 'Item Resolved', 'Item status updated successfully');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

async function adminDeleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
        await apiCall(`/items/${itemId}`, 'DELETE');
        showToast('success', 'Item Deleted', 'Item has been deleted');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

async function adminApproveClaim(claimId) {
    try {
        await apiCall(`/admin/claims/${claimId}`, 'PUT', { status: 'approved' });
        showToast('success', 'Claim Approved', 'Claim has been approved');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

async function adminRejectClaim(claimId) {
    try {
        await apiCall(`/admin/claims/${claimId}`, 'PUT', { status: 'rejected' });
        showToast('info', 'Claim Rejected', 'Claim has been rejected');
        loadAdminDashboard();
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

// ========================================
// Notifications
// ========================================

async function updateNotificationBadge() {
    if (!currentUser) {
        document.getElementById('notificationBadge').textContent = '0';
        document.getElementById('notificationBadge').style.display = 'none';
        return;
    }
    
    try {
        const result = await apiCall('/notifications');
        document.getElementById('notificationBadge').textContent = result.unread_count;
        document.getElementById('notificationBadge').style.display = result.unread_count > 0 ? 'flex' : 'none';
    } catch (error) {
        console.error('Error updating notifications:', error);
    }
}

async function loadNotifications() {
    if (!currentUser) return;
    
    try {
        const result = await apiCall('/notifications');
        const list = document.getElementById('notificationList');
        
        if (result.notifications.length === 0) {
            list.innerHTML = '<div class="empty-state" style="padding: 20px; text-align: center;">No notifications</div>';
            return;
        }
        
        list.innerHTML = result.notifications.map(n => `
            <div class="notification-item ${n.read_status ? '' : 'unread'}" onclick="markNotificationRead(${n.id})">
                <div class="notification-icon ${n.type}">
                    ${n.type === 'lost' ? '🔍' : n.type === 'found' ? '✨' : '📋'}
                </div>
                <div class="notification-content">
                    <div class="notification-text">${n.message}</div>
                    <div class="notification-time">${formatDate(n.created_at)}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading notifications:', error);
    }
}

async function markNotificationRead(id) {
    try {
        await apiCall(`/notifications/${id}/read`, 'PUT');
        updateNotificationBadge();
        loadNotifications();
    } catch (error) {
        console.error('Error marking notification read:', error);
    }
}

async function markAllRead() {
    try {
        await apiCall('/notifications/read-all', 'PUT');
        updateNotificationBadge();
        loadNotifications();
    } catch (error) {
        console.error('Error marking all read:', error);
    }
}

// ========================================
// Helper Functions
// ========================================

function createItemCard(item) {
    const icon = getCategoryIcon(item.category);
    const typeLabel = item.type === 'lost' ? 'Lost' : 'Found';
    const statusClass = item.status === 'resolved' || item.status === 'claimed' ? 'resolved' : item.status;
    
    return `
        <div class="item-card" onclick="openItemModal(${item.id})">
            <div class="item-image">${icon}</div>
            <div class="item-body">
                <div class="item-header">
                    <h3 class="item-name">${item.name}</h3>
                    <span class="item-badge ${item.type}">${typeLabel}</span>
                </div>
                <span class="item-category">${capitalize(item.category)}</span>
                <div class="item-details">
                    <div class="item-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
                            <circle cx="12" cy="10" r="3"></circle>
                        </svg>
                        ${item.location}
                    </div>
                    <div class="item-detail">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                            <line x1="16" y1="2" x2="16" y2="6"></line>
                            <line x1="8" y1="2" x2="8" y2="6"></line>
                            <line x1="3" y1="10" x2="21" y2="10"></line>
                        </svg>
                        ${formatDate(item.date)}
                    </div>
                </div>
                <div class="item-actions" onclick="event.stopPropagation()">
                    <button class="btn btn-sm btn-secondary" onclick="openItemModal(${item.id})">View Details</button>
                </div>
            </div>
        </div>
    `;
}

function getCategoryIcon(category) {
    const icons = {
        electronics: '💻',
        books: '📚',
        clothing: '👕',
        accessories: '⌚',
        wallet: '👝',
        other: '📦'
    };
    return icons[category] || '📦';
}

function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function formatDate(date) {
    if (!date) return '';
    const d = new Date(date);
    return d.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function filterByCategory(category) {
    navigateTo('lost');
    setTimeout(() => {
        document.getElementById('lostCategoryFilter').value = category;
        filterItems('lost');
    }, 100);
}

function contactOwner(itemId) {
    showToast('info', 'Contact Information', 'Use the notification system to contact the other party');
}

async function deleteItem(itemId) {
    if (!confirm('Are you sure you want to delete this item?')) return;
    
    try {
        await apiCall(`/items/${itemId}`, 'DELETE');
        
        closeItemModal();
        showToast('success', 'Item Deleted', 'Item has been deleted');
        
        if (currentPage === 'myitems') {
            loadMyItems();
        } else if (currentPage === 'lost') {
            loadLostItems();
        } else if (currentPage === 'found') {
            loadFoundItems();
        }
    } catch (error) {
        showToast('error', 'Error', error.message);
    }
}

// ========================================
// Toast Notifications
// ========================================

function showToast(type, title, message) {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ',
        warning: '!'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <div class="toast-content">
            <div class="toast-title">${title}</div>
            <div class="toast-message">${message}</div>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
        </button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

// ========================================
// Event Listeners
// ========================================

function setupEventListeners() {
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.user-dropdown')) {
            document.getElementById('dropdownMenu').classList.remove('show');
        }
        if (!e.target.closest('.notification-btn') && !e.target.closest('.notification-panel')) {
            document.getElementById('notificationPanel').classList.add('hidden');
        }
    });
    
    window.addEventListener('scroll', () => {
        const header = document.getElementById('header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeAuthModal();
            closeItemModal();
            closeClaimModal();
        }
    });
    
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.add('hidden');
            }
        });
    });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', init);
