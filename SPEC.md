# Lost and Found Portal - College Campus

## Project Overview
- **Project Name:** CampusLost - College Lost & Found Portal
- **Type:** Single Page Web Application (Frontend Only)
- **Core Functionality:** A portal where college students can report lost items, found items, claim items, and administrators can manage the system
- **Target Users:** College students and college administrators

## UI/UX Specification

### Layout Structure

**Header (Fixed)**
- Logo (left): "CampusLost" with graduation cap icon
- Navigation (center): Home, Lost Items, Found Items, My Items
- User section (right): Login/Register buttons or User avatar with dropdown
- Height: 70px
- Background: Semi-transparent dark with blur effect

**Main Content Area**
- Full viewport height minus header
- Different views based on navigation
- Responsive container: max-width 1400px

**Footer**
- Copyright info
- Quick links
- Contact support
- Height: 80px

### Visual Design

**Color Palette**
- Primary: #1a1a2e (Deep Navy)
- Secondary: #16213e (Dark Blue)
- Accent: #e94560 (Coral Red)
- Success: #00d9a5 (Mint Green)
- Warning: #ffc93c (Golden Yellow)
- Background: #0f0f1a (Near Black)
- Surface: #1f1f3a (Card Background)
- Text Primary: #ffffff
- Text Secondary: #a0a0b8
- Border: #2d2d4a

**Typography**
- Headings: 'Clash Display', sans-serif (from CDN)
- Body: 'Satoshi', sans-serif (from CDN)
- Logo: 'Clash Display' bold
- Font sizes:
  - H1: 48px
  - H2: 36px
  - H3: 24px
  - Body: 16px
  - Small: 14px

**Spacing System**
- Base unit: 8px
- Section padding: 80px vertical
- Card padding: 24px
- Gap between cards: 24px
- Border radius: 16px (cards), 8px (buttons), 50% (avatars)

**Visual Effects**
- Glassmorphism on cards (backdrop-filter: blur)
- Subtle gradient overlays on hero sections
- Smooth hover transitions (0.3s ease)
- Floating animation on hero elements
- Card hover: slight lift with shadow increase
- Gradient text on headings
- Subtle grain texture overlay on background

### Responsive Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Components

**1. Navigation Bar**
- States: Default, Scrolled (more opaque), Mobile (hamburger menu)
- Active link indicator with accent color
- User dropdown with avatar

**2. Cards (Item Cards)**
- Image thumbnail (16:9 ratio)
- Item name (bold)
- Category badge
- Date posted
- Location
- Status indicator (Lost/Found/Claimed)
- Hover: Scale up slightly, enhanced shadow

**3. Buttons**
- Primary: Accent background, white text
- Secondary: Transparent with border
- States: Default, Hover (brighten), Active (darken), Disabled (opacity 0.5)

**4. Form Inputs**
- Dark background (#1f1f3a)
- Focus: Accent border glow
- Labels above inputs
- Error state: Red border with message

**5. Modal/Dialog**
- Centered overlay
- Glassmorphism background
- Close button (top right)
- Smooth fade-in animation

**6. Notifications**
- Toast notifications (top right)
- Slide in from right
- Auto-dismiss after 5 seconds
- Types: Success (green), Error (red), Info (blue), Warning (yellow)

**7. Tabs**
- Underline style
- Animated indicator slide
- Active tab highlighted with accent

## Functionality Specification

### User Module

**Registration**
- Fields: Full Name, Email, Phone, Password, Confirm Password
- Email validation
- Password strength indicator
- Success: Redirect to login

**Login**
- Fields: Email, Password
- Remember me checkbox
- Forgot password link (UI only)
- Demo accounts available

**User Dashboard**
- Welcome message with user name
- Quick stats: My Lost Items, My Found Items, Pending Claims
- Recent activity feed
- Quick action buttons

### Lost Item Module

**Report Lost Item**
- Fields: Item Name, Category, Description, Last Seen Location, Last Seen Date, Image Upload (simulated)
- Categories: Electronics, Books, Clothing, Accessories, Wallet/Purse, ID/Cards, Other
- Form validation
- Success notification

**Browse Lost Items**
- Grid view of all lost items
- Filter by: Category, Date Range, Location
- Search by keyword
- Sort by: Newest, Oldest
- Pagination (load more button)

**Item Detail**
- Full description
- Image gallery
- Contact owner button
- "I found this" button

### Found Item Module

**Report Found Item**
- Fields: Item Name, Category, Description, Found Location, Found Date, Image Upload (simulated)
- Similar to Lost Item form

**Browse Found Items**
- Similar to Lost Items view
- "This is mine" claim button
- Contact finder button

**Claim Item**
- Fill claim form with proof of ownership
- Admin approval required (simulated)

### Admin Module

**Admin Login**
- Special admin credentials
- Dashboard access

**Admin Dashboard**
- Stats: Total Users, Lost Items, Found Items, Pending Claims
- Recent activity
- Quick actions

**Manage Items**
- View all items
- Approve/reject new items
- Edit/delete items
- Mark as resolved

**Manage Users**
- View all users
- Disable/enable users
- View user activity

### Notification Module

**Notification Types**
- New item posted (relevant category)
- Item claimed
- Claim approved/rejected
- Item found (for lost item owners)
- Item claimed (for found item reporters)

**Notification Center**
- Bell icon in header with count badge
- Dropdown with recent notifications
- Mark as read
- View all notifications page

## Pages/Views

1. **Home Page**
   - Hero section with animated text
   - Quick stats
   - Recent lost/found items
   - Call to action buttons

2. **Lost Items Page**
   - Filter sidebar
   - Items grid
   - Load more

3. **Found Items Page**
   - Same layout as Lost Items

4. **Item Detail Modal**
   - Full information
   - Action buttons

5. **Report Item Page**
   - Tab selection (Lost/Found)
   - Form

6. **User Dashboard**
   - Personal stats
   - My items list
   - Claims status

7. **Admin Dashboard**
   - Admin stats
   - Management tables

8. **Login/Register Modal**
   - Tab switching
   - Form fields

## Acceptance Criteria

1. ✅ All 5 modules are implemented with full functionality
2. ✅ Responsive design works on mobile, tablet, and desktop
3. ✅ All forms have validation and proper error handling
4. ✅ Smooth animations and transitions throughout
5. ✅ Color scheme matches specification exactly
6. ✅ All interactive elements have hover/active states
7. ✅ Navigation works without page reload (SPA)
8. ✅ Local storage used for data persistence (demo)
9. ✅ No console errors
10. ✅ Professional, polished appearance
