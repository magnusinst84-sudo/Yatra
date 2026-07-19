# Frontend Architecture & Audit

## File-Based Routing Structure
The frontend uses conditional state-based routing rather than a formal library like `react-router-dom`.

### 1. `App.tsx` (Entry Point)
* **Wired Components:** `<LandingPage>` (if unauthenticated), `<Dashboard>` (if authenticated), and `<WalkthroughModal>` (conditionally on shared links).
* **API Calls:** Calls `getSharedWalkthrough(slug)` if the URL path matches `/shared/[slug]`.
* **Guest Shared-Link Verification:**
  - **Trace:** When a user visits `/shared/aB3x9Q21`, the `useEffect` on Mount splits `window.location.pathname`.
  - It extracts `aB3x9Q21` and calls `getSharedWalkthrough(slug)`.
  - If successful, it sets `sharedWalkthrough` state.
  - The `<WalkthroughModal>` is then rendered at the bottom of the component tree with an overlay, allowing guests to view it without being redirected to a login screen. **Status: WORKING & CONFIRMED**.

### 2. `Dashboard.jsx`
* **Wired Components:** `<Navbar>`, `<Home>`, `<History>`.
* **Logic:** Uses local state `currentPage` to toggle between the `'home'` and `'history'` views.

### 3. `pages/Home.jsx` (Museum Gallery & Search)
* **Wired Components:** Hardcoded hero cards, `<WalkthroughModal>`.
* **API Calls:** 
  - Calls `startWalkthrough(searchPlace, selectedEra, idToken)` when the "Search Timeline" button is pressed.
* **Status:** Confirmed wired. Displays loading overlay while generating, then passes the resulting object into `<WalkthroughModal>`.

### 4. `pages/History.jsx`
* **Wired Components:** `<WalkthroughModal>`.
* **API Calls:** 
  - Calls `getMyWalkthroughs(idToken)` inside `useEffect` on mount.
* **Status:** Confirmed wired. Renders thumbnail cards, clicking a card calls `getWalkthroughById(wt.walkthrough_id)` and opens the modal.

### 5. `components/WalkthroughModal.jsx`
* **Wired Components:** None (leaf node overlay).
* **API Calls:** 
  - `saveWalkthrough(walkthrough_id, idToken)` when clicking "Save".
  - `shareWalkthrough(walkthrough_id, idToken)` when clicking "Share".
* **Sync Match:** Payload shapes match backend exactly.

### Built but Not Wired
* *No orphaned components found in the `frontend/src/pages` or `frontend/src/components` directories.*
