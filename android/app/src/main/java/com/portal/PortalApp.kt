package com.portal

import android.app.Application
import com.portal.data.api.PortalApiClient
import com.portal.data.repository.PortalRepository

class PortalApp : Application() {
    lateinit var repository: PortalRepository
        private set

    override fun onCreate() {
        super.onCreate()
        instance = this
        val apiClient = PortalApiClient(this)
        repository = PortalRepository(apiClient)
    }

    companion object {
        lateinit var instance: PortalApp
            private set

        // Server base URL - change this to your server IP
        const val DEFAULT_BASE_URL = "http://192.168.31.156:8080"
    }
}
