import streamlit as st
import pandas as pd
from ticketing import (
    init_db, create_ticket, get_all_tickets,
    update_ticket_status, delete_ticket, get_ticket_stats
)
from network import ping_host, scan_ports, dns_lookup, COMMON_PORTS
from monitor import (
    get_cpu_info, get_memory_info, get_disk_info,
    get_top_processes, get_network_stats, get_system_info
)

# ── Page config ──
st.set_page_config(
    page_title="IT Support Toolkit",
    page_icon="🛠️",
    layout="wide"
)

# Initialise database
init_db()

# ── Sidebar navigation ──
st.sidebar.title("🛠️ IT Support Toolkit")
st.sidebar.markdown("---")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Dashboard", "🎫 1st Line — Ticketing", "🌐 2nd Line — Network Diagnostics", "📊 3rd Line — System Monitor"]
)
st.sidebar.markdown("---")
st.sidebar.markdown("**Built by:** Anudeep Burra")
st.sidebar.markdown("**Tech:** Python · SQLite · psutil · Streamlit")

# ═══════════════════════════════════
# PAGE 1 — DASHBOARD
# ═══════════════════════════════════
if page == "🏠 Dashboard":
    st.title("🛠️ IT Support Toolkit")
    st.markdown("A unified helpdesk, network diagnostic, and system monitoring dashboard.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("### 🎫 1st Line Support")
        st.markdown("""
        **Helpdesk Ticketing System**
        - Create and manage support tickets
        - Set priority: Low / Medium / High / Critical
        - Track status: Open / In Progress / Closed
        - Filter and search tickets
        - SQLite database storage
        """)

    with col2:
        st.markdown("### 🌐 2nd Line Support")
        st.markdown("""
        **Network Diagnostic Tool**
        - Ping any host or IP address
        - Scan open/closed ports
        - DNS lookup with A, MX, TXT records
        - Common ports reference guide
        """)

    with col3:
        st.markdown("### 📊 3rd Line Support")
        st.markdown("""
        **System Monitoring Dashboard**
        - Live CPU and RAM usage
        - Disk usage with alerts at 80%+
        - Top 10 processes by CPU
        - Network I/O statistics
        - System info and uptime
        """)

    st.markdown("---")
    st.info("👈 Use the sidebar to navigate between the three support levels.")

# ═══════════════════════════════════
# PAGE 2 — TICKETING
# ═══════════════════════════════════
elif page == "🎫 1st Line — Ticketing":
    st.title("🎫 Helpdesk Ticketing System")
    st.markdown("---")

    # Ticket stats
    status_counts, priority_counts = get_ticket_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Open", status_counts.get("Open", 0))
    col2.metric("In Progress", status_counts.get("In Progress", 0))
    col3.metric("Closed", status_counts.get("Closed", 0))
    col4.metric("Critical", priority_counts.get("Critical", 0))

    st.markdown("---")
    tab1, tab2 = st.tabs(["📋 View Tickets", "➕ Create Ticket"])

    # ── View Tickets ──
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "In Progress", "Closed"])
        with col2:
            priority_filter = st.selectbox("Filter by Priority", ["All", "Critical", "High", "Medium", "Low"])

        tickets = get_all_tickets(status_filter, priority_filter)

        if not tickets:
            st.info("No tickets found. Create one in the 'Create Ticket' tab!")
        else:
            for ticket in tickets:
                tid, title, desc, priority, status, assigned, created, updated = ticket

                # Priority colour
                priority_color = {"Critical": "🔴", "High": "🟠", "Medium": "🟡", "Low": "🟢"}.get(priority, "⚪")
                status_color   = {"Open": "🔵", "In Progress": "🟡", "Closed": "✅"}.get(status, "⚪")

                with st.expander(f"{priority_color} [{priority}] #{tid} — {title}  |  {status_color} {status}"):
                    st.markdown(f"**Description:** {desc}")
                    st.markdown(f"**Assigned to:** {assigned or 'Unassigned'}")
                    st.markdown(f"**Created:** {created}  |  **Updated:** {updated}")

                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        new_status = st.selectbox(
                            "Update Status",
                            ["Open", "In Progress", "Closed"],
                            index=["Open", "In Progress", "Closed"].index(status),
                            key=f"status_{tid}"
                        )
                    with col2:
                        if st.button("💾 Update", key=f"update_{tid}"):
                            update_ticket_status(tid, new_status)
                            st.success(f"Ticket #{tid} updated to {new_status}")
                            st.rerun()
                    with col3:
                        if st.button("🗑️ Delete", key=f"delete_{tid}"):
                            delete_ticket(tid)
                            st.success(f"Ticket #{tid} deleted")
                            st.rerun()

    # ── Create Ticket ──
    with tab2:
        with st.form("create_ticket_form"):
            title       = st.text_input("Ticket Title *", placeholder="e.g. User cannot login to VPN")
            description = st.text_area("Description", placeholder="Describe the issue in detail...")
            col1, col2  = st.columns(2)
            with col1:
                priority    = st.selectbox("Priority *", ["Low", "Medium", "High", "Critical"])
            with col2:
                assigned_to = st.text_input("Assign To", placeholder="e.g. John Smith")
            submitted   = st.form_submit_button("➕ Create Ticket")

        if submitted:
            if not title:
                st.error("Please enter a ticket title.")
            else:
                ticket_id = create_ticket(title, description, priority, assigned_to)
                st.success(f"✅ Ticket #{ticket_id} created successfully!")

# ═══════════════════════════════════
# PAGE 3 — NETWORK DIAGNOSTICS
# ═══════════════════════════════════
elif page == "🌐 2nd Line — Network Diagnostics":
    st.title("🌐 Network Diagnostic Tool")
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs(["📡 Ping Host", "🔍 Port Scanner", "🌍 DNS Lookup"])

    # ── Ping ──
    with tab1:
        st.subheader("📡 Ping Host")
        host = st.text_input("Enter hostname or IP", placeholder="e.g. google.com or 8.8.8.8")
        if st.button("🚀 Run Ping"):
            if not host:
                st.error("Please enter a hostname or IP address.")
            else:
                with st.spinner(f"Pinging {host}..."):
                    success, output = ping_host(host)
                if success:
                    st.success(f"✅ {host} is reachable!")
                else:
                    st.error(f"❌ {host} is unreachable.")
                st.code(output)

    # ── Port Scanner ──
    with tab2:
        st.subheader("🔍 Port Scanner")
        col1, col2 = st.columns(2)
        with col1:
            scan_host = st.text_input("Host to scan", placeholder="e.g. google.com")
        with col2:
            scan_mode = st.selectbox("Scan Mode", ["Common Ports", "Custom Ports"])

        if scan_mode == "Custom Ports":
            custom_ports = st.text_input("Enter ports (comma separated)", placeholder="80,443,22,3306")

        if st.button("🔍 Scan Ports"):
            if not scan_host:
                st.error("Please enter a host to scan.")
            else:
                if scan_mode == "Common Ports":
                    ports = list(COMMON_PORTS.keys())
                else:
                    try:
                        ports = [int(p.strip()) for p in custom_ports.split(",")]
                    except ValueError:
                        st.error("Invalid port numbers. Please enter comma-separated numbers.")
                        st.stop()

                with st.spinner(f"Scanning {scan_host}..."):
                    results = scan_ports(scan_host, ports)

                open_ports   = {p: s for p, s in results.items() if s == "Open"}
                closed_ports = {p: s for p, s in results.items() if s == "Closed"}

                col1, col2 = st.columns(2)
                col1.metric("Open Ports", len(open_ports))
                col2.metric("Closed Ports", len(closed_ports))

                df = pd.DataFrame([
                    {
                        "Port": port,
                        "Service": COMMON_PORTS.get(port, "Unknown"),
                        "Status": status
                    }
                    for port, status in results.items()
                ])
                st.dataframe(df, use_container_width=True)

    # ── DNS Lookup ──
    with tab3:
        st.subheader("🌍 DNS Lookup")
        domain = st.text_input("Enter domain name", placeholder="e.g. google.com")
        if st.button("🔎 Lookup DNS"):
            if not domain:
                st.error("Please enter a domain name.")
            else:
                with st.spinner(f"Looking up {domain}..."):
                    results = dns_lookup(domain)
                if "Error" in results:
                    st.error(results["Error"])
                else:
                    for record_type, values in results.items():
                        st.markdown(f"**{record_type}:**")
                        if isinstance(values, list):
                            for v in values:
                                st.code(v)
                        else:
                            st.code(values)

# ═══════════════════════════════════
# PAGE 4 — SYSTEM MONITOR
# ═══════════════════════════════════
elif page == "📊 3rd Line — System Monitor":
    st.title("📊 System Monitoring Dashboard")
    st.markdown("---")

    # Auto-refresh
    auto_refresh = st.checkbox("🔄 Auto-refresh every 5 seconds")
    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()

    # System info
    sys_info = get_system_info()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("OS", sys_info["os"])
    col2.metric("Hostname", sys_info["hostname"])
    col3.metric("Uptime", sys_info["uptime"])
    col4.metric("Architecture", sys_info["architecture"])

    st.markdown("---")

    # CPU and RAM
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🖥️ CPU Usage")
        cpu = get_cpu_info()
        st.metric("Overall CPU Usage", f"{cpu['usage_percent']}%")
        st.progress(cpu["usage_percent"] / 100)
        st.markdown(f"**Cores:** {cpu['core_count']}  |  **Threads:** {cpu['thread_count']}  |  **Frequency:** {cpu['frequency']} MHz")
        if cpu["per_core"]:
            st.markdown("**Per Core Usage:**")
            for i, usage in enumerate(cpu["per_core"]):
                st.progress(usage / 100, text=f"Core {i+1}: {usage}%")

    with col2:
        st.subheader("💾 Memory Usage")
        mem = get_memory_info()
        st.metric("RAM Usage", f"{mem['percent']}%", f"{mem['used_gb']} GB / {mem['total_gb']} GB")
        st.progress(mem["percent"] / 100)
        st.metric("Swap Usage", f"{mem['swap_percent']}%", f"{mem['swap_used_gb']} GB / {mem['swap_total_gb']} GB")
        if mem["swap_total_gb"] > 0:
            st.progress(mem["swap_percent"] / 100)

    st.markdown("---")

    # Disk usage
    st.subheader("💿 Disk Usage")
    disks = get_disk_info()
    for disk in disks:
        col1, col2 = st.columns([3, 1])
        with col1:
            label = f"{disk['device']} ({disk['mountpoint']}) — {disk['used_gb']} GB / {disk['total_gb']} GB"
            color = "🔴" if disk["alert"] else "🟢"
            st.markdown(f"{color} **{label}**")
            st.progress(disk["percent"] / 100)
        with col2:
            if disk["alert"]:
                st.error(f"⚠️ {disk['percent']}% — Low disk space!")
            else:
                st.success(f"✅ {disk['percent']}% used")

    st.markdown("---")

    # Top processes
    st.subheader("⚙️ Top 10 Processes by CPU")
    processes = get_top_processes()
    df = pd.DataFrame(processes)
    st.dataframe(df, use_container_width=True)

    st.markdown("---")

    # Network stats
    st.subheader("🌐 Network I/O")
    net = get_network_stats()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Data Sent", f"{net['bytes_sent_mb']} MB")
    col2.metric("Data Received", f"{net['bytes_recv_mb']} MB")
    col3.metric("Packets Sent", net["packets_sent"])
    col4.metric("Packets Received", net["packets_recv"])