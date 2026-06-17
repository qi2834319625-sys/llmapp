import Foundation
import SwiftUI

// MARK: - API Service
class APIService {
    static let shared = APIService()
    private let baseURL = "http://192.168.31.156:8080"
    private init() {}

    func login(username: String, password: String) async throws -> AuthResponse {
        let url = URL(string: "\(baseURL)/api/auth/login")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body = ["username": username, "password": password]
        request.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(AuthResponse.self, from: data)
    }

    func verifyToken(_ token: String) async throws -> Bool {
        let url = URL(string: "\(baseURL)/api/auth/verify")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, _) = try await URLSession.shared.data(for: request)
        let response = try JSONDecoder().decode(VerifyResponse.self, from: data)
        return response.valid
    }

    func getDashboardStats(token: String) async throws -> DashboardStats {
        let url = URL(string: "\(baseURL)/api/dashboard/stats")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(DashboardStats.self, from: data)
    }

    func get<T: Codable>(path: String, token: String) async throws -> T {
        let url = URL(string: "\(baseURL)\(path)")!
        var request = URLRequest(url: url)
        request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        let (data, _) = try await URLSession.shared.data(for: request)
        return try JSONDecoder().decode(T.self, from: data)
    }
}

// MARK: - Auth Manager
class AuthManager: ObservableObject {
    @Published var isLoggedIn = false
    @Published var token = ""
    @Published var username = ""

    private let tokenKey = "auth_token"
    private let usernameKey = "username"

    init() {
        token = UserDefaults.standard.string(forKey: tokenKey) ?? ""
        username = UserDefaults.standard.string(forKey: usernameKey) ?? ""
        if !token.isEmpty {
            Task { await verifyToken() }
        }
    }

    func login(username: String, password: String) async -> Result<String, Error> {
        do {
            let response = try await APIService.shared.login(username: username, password: password)
            if response.success {
                self.token = response.token
                self.username = username
                self.isLoggedIn = true
                // 只存 token 和用户名，不存密码
                UserDefaults.standard.set(response.token, forKey: tokenKey)
                UserDefaults.standard.set(username, forKey: usernameKey)
                return .success(response.token)
            } else {
                return .failure(NSError(domain: "", code: 401, userInfo: [NSLocalizedDescriptionKey: response.error]))
            }
        } catch {
            return .failure(error)
        }
    }

    func logout() {
        token = ""
        username = ""
        isLoggedIn = false
        UserDefaults.standard.removeObject(forKey: tokenKey)
        UserDefaults.standard.removeObject(forKey: usernameKey)
    }

    private func verifyToken() async {
        do {
            let valid = try await APIService.shared.verifyToken(token)
            DispatchQueue.main.async { self.isLoggedIn = valid }
        } catch {
            DispatchQueue.main.async { self.isLoggedIn = false }
        }
    }
}

// MARK: - Models
struct AuthResponse: Codable {
    let success: Bool
    let token: String
    let username: String
    let error: String
}

struct VerifyResponse: Codable {
    let valid: Bool
    let username: String
}

struct DashboardStats: Codable {
    let recruitmentQuestions: Int
    let githubRepos: Int
    let youtubeResources: Int
    let cryptoPapers: Int
    let mangaProjects: Int
    let mangaScenes: Int
    let investmentRecords: Int
    let recipes: Int
    let fashionItems: Int
    let makeupTips: Int
    let cetExamItems: Int
    let civilExamTopics: Int
    let studyAbroad: Int

    enum CodingKeys: String, CodingKey {
        case recruitmentQuestions = "recruitment_questions"
        case githubRepos = "github_repos"
        case youtubeResources = "youtube_resources"
        case cryptoPapers = "crypto_papers"
        case mangaProjects = "manga_projects"
        case mangaScenes = "manga_scenes"
        case investmentRecords = "investment_records"
        case recipes
        case fashionItems = "fashion_items"
        case makeupTips = "makeup_tips"
        case cetExamItems = "cet_exam_items"
        case civilExamTopics = "civil_exam_topics"
        case studyAbroad = "study_abroad"
    }
}
