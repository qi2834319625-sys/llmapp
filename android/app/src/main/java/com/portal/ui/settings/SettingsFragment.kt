package com.portal.ui.settings

import android.content.Intent
import android.os.Bundle
import android.view.Gravity
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Button
import android.widget.EditText
import android.widget.LinearLayout
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.fragment.app.Fragment
import com.portal.R
import com.portal.ui.auth.LoginActivity

class SettingsFragment : Fragment() {

    private lateinit var containerLayout: LinearLayout
    private lateinit var prefs: android.content.SharedPreferences

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_settings, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        containerLayout = view.findViewById(R.id.settings_container)
        prefs = requireContext().getSharedPreferences("portal_prefs", android.content.Context.MODE_PRIVATE)

        buildSettingsItems()
    }

    private fun buildSettingsItems() {
        containerLayout.removeAllViews()

        // Server URL
        addPreferenceItem(
            title = "Server URL",
            subtitle = prefs.getString("server_url", "http://192.168.31.156:8080") ?: "http://192.168.31.156:8080",
            onClick = { showServerUrlDialog() }
        )

        // Username (display only)
        addPreferenceItem(
            title = "Username",
            subtitle = prefs.getString("username", "") ?: "",
            onClick = null
        )

        // Version
        addPreferenceItem(
            title = "Version",
            subtitle = "1.0.0",
            onClick = null
        )

        // Clear Cache
        addPreferenceItem(
            title = "Clear Cache",
            subtitle = "Clear all cached data",
            onClick = {
                clearCache()
                Toast.makeText(requireContext(), "Cache cleared", Toast.LENGTH_SHORT).show()
            }
        )

        // Logout
        addPreferenceItem(
            title = "Logout",
            subtitle = "Sign out and return to login",
            onClick = { performLogout() }
        )
    }

    private fun addPreferenceItem(title: String, subtitle: String, onClick: (() -> Unit)?) {
        val context = requireContext()

        val itemLayout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(dp(16), dp(12), dp(16), dp(12))
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                LinearLayout.LayoutParams.WRAP_CONTENT
            )
        }

        val titleView = TextView(context).apply {
            text = title
            textSize = 16f
            setTypeface(null, android.graphics.Typeface.BOLD)
            setTextColor(context.getColor(android.R.color.primary_text_light))
        }

        val subtitleView = TextView(context).apply {
            text = subtitle
            textSize = 13f
            setTextColor(context.getColor(android.R.color.secondary_text_light))
            setPadding(0, dp(4), 0, 0)
        }

        itemLayout.addView(titleView)
        itemLayout.addView(subtitleView)

        if (onClick != null) {
            itemLayout.isClickable = true
            itemLayout.isFocusable = true
            itemLayout.setOnClickListener { onClick() }

            // Add ripple/selector background
            val typedValue = android.util.TypedValue()
            context.theme.resolveAttribute(android.R.attr.selectableItemBackground, typedValue, true)
            itemLayout.setBackgroundResource(typedValue.resourceId)
        }

        containerLayout.addView(itemLayout)

        // Divider
        val divider = View(context).apply {
            layoutParams = LinearLayout.LayoutParams(
                LinearLayout.LayoutParams.MATCH_PARENT,
                1
            ).apply {
                setMargins(dp(16), 0, dp(16), 0)
            }
            setBackgroundColor(context.getColor(android.R.color.darker_gray))
            alpha = 0.3f
        }
        containerLayout.addView(divider)
    }

    private fun showServerUrlDialog() {
        val context = requireContext()
        val editText = EditText(context).apply {
            setText(prefs.getString("server_url", "http://192.168.31.156:8080"))
            setPadding(dp(24), dp(16), dp(24), dp(8))
        }

        AlertDialog.Builder(context)
            .setTitle("Server URL")
            .setView(editText)
            .setPositiveButton("Save") { _, _ ->
                val newUrl = editText.text.toString().trim()
                if (newUrl.isNotEmpty()) {
                    prefs.edit().putString("server_url", newUrl).apply()
                    prefs.edit().putString("server_url", newUrl).apply()
                    buildSettingsItems()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    private fun clearCache() {
        requireContext().cacheDir.deleteRecursively()
    }

    private fun performLogout() {
        prefs.edit().clear().apply()

        val intent = Intent(requireContext(), LoginActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        }
        startActivity(intent)
        requireActivity().finish()
    }

    private fun dp(value: Int): Int {
        return (value * resources.displayMetrics.density).toInt()
    }
}
