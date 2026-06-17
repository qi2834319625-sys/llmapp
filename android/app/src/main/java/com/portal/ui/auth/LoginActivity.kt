package com.portal.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.ui.dashboard.DashboardActivity
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class LoginActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_login)

        val etServerUrl = findViewById<EditText>(R.id.et_server_url)
        val etUsername = findViewById<EditText>(R.id.et_username)
        val etPassword = findViewById<EditText>(R.id.et_password)
        val btnLogin = findViewById<Button>(R.id.btn_login)
        val progressBar = findViewById<ProgressBar>(R.id.progress_bar)

        // Load saved values
        val prefs = getSharedPreferences("portal_prefs", MODE_PRIVATE)
        etServerUrl?.setText(prefs.getString("server_url", "http://192.168.31.156:8080"))
        etUsername?.setText(prefs.getString("username", ""))

        btnLogin?.setOnClickListener {
            val serverUrl = etServerUrl?.text.toString().trim()
            val username = etUsername?.text.toString().trim()
            val password = etPassword?.text.toString().trim()

            if (serverUrl.isEmpty() || username.isEmpty() || password.isEmpty()) {
                Snackbar.make(findViewById(android.R.id.content), "请填写所有字段", Snackbar.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            progressBar?.visibility = View.VISIBLE
            btnLogin.isEnabled = false

            GlobalScope.launch {
                try {
                    val response = PortalApp.instance.repository.login(username, password)
                    runOnUiThread {
                        progressBar?.visibility = View.GONE
                        btnLogin.isEnabled = true
                        if (response.success) {
                            prefs.edit()
                                .putString("auth_token", response.token)
                                .putString("username", username)
                                .putString("server_url", serverUrl)
                                .apply()
                            startActivity(Intent(this@LoginActivity, DashboardActivity::class.java))
                            finish()
                        } else {
                            Snackbar.make(findViewById(android.R.id.content), "登录失败: ${response.error}", Snackbar.LENGTH_SHORT).show()
                        }
                    }
                } catch (e: Exception) {
                    runOnUiThread {
                        progressBar?.visibility = View.GONE
                        btnLogin.isEnabled = true
                        Snackbar.make(findViewById(android.R.id.content), "网络错误: ${e.message}", Snackbar.LENGTH_SHORT).show()
                    }
                }
            }
        }
    }
}
