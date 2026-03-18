let selectedFolderPath = ""


// ── THEME ────────────────────────────────────────────────────

function toggleTheme() {
    const html = document.documentElement
    const next = html.getAttribute("data-theme") === "dark" ? "light" : "dark"
    html.setAttribute("data-theme", next)
    localStorage.setItem("fileflow-theme", next)
}

function loadTheme() {
    const saved = localStorage.getItem("fileflow-theme") || "dark"
    document.documentElement.setAttribute("data-theme", saved)
}


// ── BROWSE ───────────────────────────────────────────────────

async function browseFolder() {
    const browseBtn         = document.getElementById("browseBtn")
    const browseBtnText     = document.getElementById("browseBtnText")
    const browseLoader      = document.getElementById("browseLoader")
    const pathDisplay       = document.getElementById("pathDisplay")
    const pathText          = document.getElementById("pathText")
    const folderConfirm     = document.getElementById("folderConfirm")
    const folderConfirmText = document.getElementById("folderConfirmText")
    const organizeBtn       = document.getElementById("organizeBtn")

    hideError()
    browseBtn.disabled = true
    browseBtnText.classList.add("hidden")
    browseLoader.classList.remove("hidden")

    try {
        const res  = await fetch("/browse")
        const data = await res.json()

        if (data.success && data.path) {
            selectedFolderPath = data.path
            pathText.textContent = data.path
            pathText.className   = "path-value"
            pathDisplay.classList.add("has-path")

            const name = data.path.split(/[/\\]/).filter(Boolean).pop()
            folderConfirmText.textContent = `"${name}" selected — ready to organize`
            folderConfirm.classList.remove("hidden")
            organizeBtn.disabled = false
        }
    } catch {
        showError("Could not open folder browser. Is Flask running?")
    } finally {
        browseBtn.disabled = false
        browseBtnText.classList.remove("hidden")
        browseLoader.classList.add("hidden")
    }
}


// ── ORGANIZE ─────────────────────────────────────────────────

async function startOrganize() {
    const organizeBtn       = document.getElementById("organizeBtn")
    const organizeBtnText   = document.getElementById("organizeBtnText")
    const organizeBtnLoader = document.getElementById("organizeBtnLoader")

    hideError()
    organizeBtn.disabled = true
    organizeBtnText.classList.add("hidden")
    organizeBtnLoader.classList.remove("hidden")

    const includeSubfolders = document.getElementById("includeSubfolders").checked

    try {
        const res  = await fetch("/organize", {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({ folder_path: selectedFolderPath, include_subfolders: includeSubfolders }),
        })
        const data = await res.json()

        if (data.success) {
            window.location.href = data.redirect
        } else {
            showError(data.error || "Something went wrong.")
            organizeBtn.disabled = false
            organizeBtnText.classList.remove("hidden")
            organizeBtnLoader.classList.add("hidden")
        }
    } catch {
        showError("Network error. Is Flask running?")
        organizeBtn.disabled = false
        organizeBtnText.classList.remove("hidden")
        organizeBtnLoader.classList.add("hidden")
    }
}


// ── HELPERS ──────────────────────────────────────────────────

function showError(msg) {
    document.getElementById("errorText").textContent = msg
    document.getElementById("errorMsg").classList.remove("hidden")
}

function hideError() {
    document.getElementById("errorMsg").classList.add("hidden")
}


// ── INIT ─────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", loadTheme)
