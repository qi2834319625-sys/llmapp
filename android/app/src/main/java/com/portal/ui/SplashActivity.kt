package com.portal.ui

import android.content.Intent
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import androidx.appcompat.app.AppCompatActivity
import com.portal.PortalApp
import com.portal.R
import com.portal.ui.auth.LoginActivity
import com.portal.ui.dashboard.DashboardActivity
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_splash)

        Handler(Looper.getMainLooper()).postDelayed({
            checkAuth()
        }, 1500)
    }

    private fun checkAuth() {
        GlobalScope.launch {
            try {
                val valid = PortalApp.instance.repository.verifyToken()
                runOnUiThread {
                    if (valid) {
                        startActivity(Intent(this@SplashActivity, DashboardActivity::class.java))
                    } else {
                        startActivity(Intent(this@SplashActivity, LoginActivity::class.java))
                    }
                    finish()
                }
            } catch (e: Exception) {
                runOnUiThread {
                    startActivity(Intent(this@SplashActivity, LoginActivity::class.java))
                    finish()
                }
            }
        }
    }
}
