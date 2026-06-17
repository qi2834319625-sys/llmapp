import SwiftUI

struct LoginView: View {
    @EnvironmentObject var authManager: AuthManager
    @State private var username = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var errorMessage = ""

    var body: some View {
        ZStack {
            // 背景渐变
            LinearGradient(
                colors: [Color(red: 0.4, green: 0.2, blue: 0.8), Color(red: 0.2, green: 0.1, blue: 0.5)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 24) {
                Spacer()

                // Logo
                Text("🔐")
                    .font(.system(size: 72))

                Text("多系统智能门户")
                    .font(.title)
                    .fontWeight(.bold)
                    .foregroundColor(.white)

                Spacer().frame(height: 32)

                // 用户名
                TextField("用户名", text: $username)
                    .textFieldStyle(.plain)
                    .padding()
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)
                    .foregroundColor(.white)
                    .autocapitalization(.none)
                    .disableAutocorrection(true)

                // 密码
                SecureField("密码", text: $password)
                    .textFieldStyle(.plain)
                    .padding()
                    .background(Color.white.opacity(0.2))
                    .cornerRadius(12)
                    .foregroundColor(.white)

                // 错误信息
                if !errorMessage.isEmpty {
                    Text(errorMessage)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                // 登录按钮
                Button(action: doLogin) {
                    if isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .black))
                    } else {
                        Text("登 录")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .frame(height: 52)
                .background(Color(red: 0.0, green: 0.8, blue: 0.7))
                .foregroundColor(.black)
                .cornerRadius(12)
                .disabled(isLoading)

                Spacer()
            }
            .padding(.horizontal, 32)
        }
    }

    private func doLogin() {
        guard !username.isEmpty, !password.isEmpty else {
            errorMessage = "请输入用户名和密码"
            return
        }
        isLoading = true
        errorMessage = ""

        Task {
            let result = await authManager.login(username: username, password: password)
            DispatchQueue.main.async {
                isLoading = false
                switch result {
                case .success:
                    break // isLoggedIn 会自动更新
                case .failure(let error):
                    errorMessage = error.localizedDescription
                }
            }
        }
    }
}
