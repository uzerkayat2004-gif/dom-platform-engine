use tauri::Manager;
use std::fs::OpenOptions;
use std::io::Write;

fn append_debug_line(line: &str) {
    let primary = "C:\\Users\\Asus\\dom-platform-engine\\debug-48444a.log";
    let fallback = "C:\\Users\\Asus\\dom-platform-engine\\.cursor\\debug-48444a.log";
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(primary) {
        let _ = writeln!(file, "{}", line);
        return;
    }
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(fallback) {
        let _ = writeln!(file, "{}", line);
    }
}

fn debug_log_internal(location: &str, message: &str, data: &str, hypothesis_id: &str) {
    let line = format!(
        "{{\"sessionId\":\"48444a\",\"runId\":\"pre-fix\",\"hypothesisId\":\"{}\",\"location\":\"{}\",\"message\":\"{}\",\"data\":{},\"timestamp\":{}}}",
        hypothesis_id,
        location,
        message,
        data,
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0)
    );
    append_debug_line(&line);
}

#[tauri::command]
fn minimize_window(app: tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.minimize();
    }
}

#[tauri::command]
fn maximize_window(app: tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        if window.is_maximized().unwrap_or(false) {
            let _ = window.unmaximize();
        } else {
            let _ = window.maximize();
        }
    }
}

#[tauri::command]
fn close_window(app: tauri::AppHandle) {
    if let Some(window) = app.get_webview_window("main") {
        let _ = window.close();
    }
}

#[tauri::command]
fn debug_log_command(location: String, message: String, data: String, run_id: String, hypothesis_id: String) {
    let line = format!(
        "{{\"sessionId\":\"48444a\",\"runId\":\"{}\",\"hypothesisId\":\"{}\",\"location\":\"{}\",\"message\":\"{}\",\"data\":{},\"timestamp\":{}}}",
        run_id,
        hypothesis_id,
        location,
        message,
        data,
        std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis())
            .unwrap_or(0)
    );
    append_debug_line(&line);
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    // #region agent log
    debug_log_internal(
        "lib.rs:run",
        "Tauri run() entered",
        "{\"component\":\"tauri\"}",
        "H6",
    );
    // #endregion
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            minimize_window,
            maximize_window,
            close_window,
            debug_log_command
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
