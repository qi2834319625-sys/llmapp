import SwiftUI

struct MainTabView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("首页")
                }

            CoupleView()
                .tabItem {
                    Image(systemName: "heart.fill")
                    Text("情侣")
                }

            StudyView()
                .tabItem {
                    Image(systemName: "graduationcap.fill")
                    Text("学习")
                }

            MoreView()
                .tabItem {
                    Image(systemName: "ellipsis")
                    Text("更多")
                }
        }
    }
}

// MARK: - Dashboard
struct DashboardView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var stats = DashboardStats(
        recruitmentQuestions: 0, githubRepos: 0, youtubeResources: 0,
        cryptoPapers: 0, mangaProjects: 0, mangaScenes: 0,
        investmentRecords: 0, recipes: 0, fashionItems: 0,
        makeupTips: 0, cetExamItems: 0, civilExamTopics: 0, studyAbroad: 0
    )

    let modules = [
        ("💕", "情侣空间"),
        ("💼", "秋招备战"),
        ("🔐", "密码学论文"),
        ("🧠", "GNN匹配"),
        ("📈", "投资理财"),
        ("💄", "美妆系统"),
        ("👗", "服装搭配"),
        ("🍳", "美食厨房"),
        ("✈️", "出国规划"),
        ("📚", "考公备考"),
        ("📝", "CET考试"),
        ("🎭", "漫剧创作"),
        ("⚙️", "系统设置")
    ]

    var body: some View {
        NavigationView {
            ScrollView {
                LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 12), count: 3), spacing: 12) {
                    ForEach(modules, id:.0) { module in
                        ModuleCard(icon: module.0, name: module.1)
                    }
                }
                .padding()
            }
            .navigationTitle("Portal")
            .task {
                await loadStats()
            }
        }
    }

    private func loadStats() async {
        do {
            let s = try await APIService.shared.getDashboardStats(token: authManager.token)
            DispatchQueue.main.async { stats = s }
        } catch {}
    }
}

struct ModuleCard: View {
    let icon: String
    let name: String

    var body: some View {
        VStack(spacing: 8) {
            Text(icon)
                .font(.system(size: 32))
            Text(name)
                .font(.caption)
                .multilineTextAlignment(.center)
        }
        .frame(height: 100)
        .frame(maxWidth: .infinity)
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.1), radius: 4)
    }
}

// MARK: - Couple
struct CoupleView: View {
    var body: some View {
        NavigationView {
            Text("情侣空间")
                .navigationTitle("💕 情侣")
        }
    }
}

// MARK: - Study
struct StudyView: View {
    var body: some View {
        NavigationView {
            Text("学习中心")
                .navigationTitle("📚 学习")
        }
    }
}

// MARK: - More
struct MoreView: View {
    @EnvironmentObject var authManager: AuthManager

    var body: some View {
        NavigationView {
            List {
                Section {
                    Text("服务器: http://192.168.31.156:8080")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("用户: \(authManager.username)")
                }

                Section {
                    Button("退出登录", role: .destructive) {
                        authManager.logout()
                    }
                }
            }
            .navigationTitle("更多")
        }
    }
}
