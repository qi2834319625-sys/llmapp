package com.portal.util

import android.content.Context
import android.content.SharedPreferences

class PreferencesManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("portal_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_AUTH_TOKEN = "auth_token"
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_USERNAME = "username"
        private const val KEY_REFRESH_TOKEN = "refresh_token"
        private const val KEY_TOKEN_EXPIRES_AT = "token_expires_at"
        private const val KEY_IS_LOGGED_IN = "is_logged_in"
        private const val KEY_LAST_SYNC = "last_sync"

        private const val DEFAULT_SERVER_URL = "http://192.168.31.156:8080"

        fun getServerUrl(context: Context): String {
            return context.getSharedPreferences("portal_prefs", Context.MODE_PRIVATE)
                .getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
        }

        fun getToken(context: Context): String {
            return context.getSharedPreferences("portal_prefs", Context.MODE_PRIVATE)
                .getString(KEY_AUTH_TOKEN, "") ?: ""
        }

        fun isLoggedIn(context: Context): Boolean {
            return context.getSharedPreferences("portal_prefs", Context.MODE_PRIVATE)
                .getBoolean(KEY_IS_LOGGED_IN, false)
        }
    }

    var authToken: String
        get() = prefs.getString(KEY_AUTH_TOKEN, "") ?: ""
        set(value) = prefs.edit().putString(KEY_AUTH_TOKEN, value).apply()

    val hasToken: Boolean
        get() = authToken.isNotBlank()

    var serverUrl: String
        get() = prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
        set(value) = prefs.edit().putString(KEY_SERVER_URL, value).apply()

    var username: String
        get() = prefs.getString(KEY_USERNAME, "") ?: ""
        set(value) = prefs.edit().putString(KEY_USERNAME, value).apply()

    var refreshToken: String
        get() = prefs.getString(KEY_REFRESH_TOKEN, "") ?: ""
        set(value) = prefs.edit().putString(KEY_REFRESH_TOKEN, value).apply()

    var tokenExpiresAt: Long
        get() = prefs.getLong(KEY_TOKEN_EXPIRES_AT, 0L)
        set(value) = prefs.edit().putLong(KEY_TOKEN_EXPIRES_AT, value).apply()

    val isTokenExpired: Boolean
        get() = tokenExpiresAt > 0 && System.currentTimeMillis() >= tokenExpiresAt

    var isLoggedIn: Boolean
        get() = prefs.getBoolean(KEY_IS_LOGGED_IN, false)
        set(value) = prefs.edit().putBoolean(KEY_IS_LOGGED_IN, value).apply()

    var lastSync: Long
        get() = prefs.getLong(KEY_LAST_SYNC, 0L)
        set(value) = prefs.edit().putLong(KEY_LAST_SYNC, value).apply()

    fun saveSession(authToken: String, username: String, expiresIn: Long? = null) {
        this.authToken = authToken
        this.username = username
        this.isLoggedIn = true
        if (expiresIn != null) {
            this.tokenExpiresAt = System.currentTimeMillis() + (expiresIn * 1000)
        }
    }

    fun clearSession() {
        prefs.edit()
            .remove(KEY_AUTH_TOKEN)
            .remove(KEY_REFRESH_TOKEN)
            .remove(KEY_USERNAME)
            .remove(KEY_TOKEN_EXPIRES_AT)
            .putBoolean(KEY_IS_LOGGED_IN, false)
            .apply()
    }

    fun clearAll() {
        prefs.edit().clear().apply()
    }
}
