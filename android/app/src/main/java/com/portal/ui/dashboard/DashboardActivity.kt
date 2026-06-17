package com.portal.ui.dashboard

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.portal.R
import com.portal.ui.couple.CoupleFragment
import com.portal.ui.dashboard.DashboardFragment
import com.portal.ui.more.MoreFragment
import com.portal.ui.study.StudyFragment

class DashboardActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.nav_host_fragment, DashboardFragment())
                .commit()
        }

        findViewById<com.google.android.material.bottomnavigation.BottomNavigationView>(R.id.bottom_nav)?.setOnItemSelectedListener { item ->
            val fragment = when (item.itemId) {
                R.id.nav_home -> DashboardFragment()
                R.id.nav_couple -> CoupleFragment()
                R.id.nav_study -> StudyFragment()
                R.id.nav_more -> MoreFragment()
                else -> return@setOnItemSelectedListener false
            }
            supportFragmentManager.beginTransaction()
                .replace(R.id.nav_host_fragment, fragment)
                .commit()
            true
        }
    }
}
