import { Outlet, NavLink, useLocation } from "react-router-dom";
import styles from "./Layout.module.css";

const NAV_ITEMS = [
  {
    to: "/reports",
    label: "Reports",
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
        <polyline points="14 2 14 8 20 8"/>
        <line x1="16" y1="13" x2="8" y2="13"/>
        <line x1="16" y1="17" x2="8" y2="17"/>
        <polyline points="10 9 9 9 8 9"/>
      </svg>
    ),
  },
];

export default function Layout() {
  return (
    <div className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>
          <div className={styles.brandIcon}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
          </div>
          <span className={styles.brandName}>ReportHub</span>
        </div>

        <nav className={styles.nav}>
          <p className={styles.navLabel}>Platform</p>
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `${styles.navItem} ${isActive ? styles.navItemActive : ""}`
              }
            >
              <span className={styles.navIcon}>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className={styles.sidebarFooter}>
          <div className={styles.versionBadge}>v0.1.0</div>
        </div>
      </aside>

      <div className={styles.main}>
        <header className={styles.topbar}>
          <div className={styles.topbarInner}>
            <Breadcrumb />
            <div className={styles.topbarRight}>
              <div className={styles.statusDot} title="All systems operational" />
              <span className={styles.statusText}>Operational</span>
            </div>
          </div>
        </header>

        <main className={styles.content}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}

function Breadcrumb() {
  const location = useLocation();
  const parts = location.pathname.split("/").filter(Boolean);

  return (
    <nav className={styles.breadcrumb} aria-label="Breadcrumb">
      {parts.map((part, i) => (
        <span key={i} className={styles.breadcrumbItem}>
          {i > 0 && <span className={styles.breadcrumbSep}>/</span>}
          <span className={i === parts.length - 1 ? styles.breadcrumbCurrent : styles.breadcrumbPart}>
            {part.charAt(0).toUpperCase() + part.slice(1)}
          </span>
        </span>
      ))}
    </nav>
  );
}
