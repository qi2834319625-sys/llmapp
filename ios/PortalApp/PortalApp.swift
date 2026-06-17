import SwiftUI

@main
struct PortalApp: App {
    @StateObject private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            if authManager.isLoggedIn {
                MainTabView()
                    .environmentObject(authManager)
            } else {
                LoginView()
                    .environmentObject(authManager)
            }
        }
    }
}
