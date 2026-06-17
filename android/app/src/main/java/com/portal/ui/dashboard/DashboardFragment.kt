package com.portal.ui.dashboard

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.google.android.material.card.MaterialCardView
import com.google.android.material.snackbar.Snackbar
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.DashboardStats
import com.portal.data.repository.Resource
import com.portal.ui.cetexam.CetExamFragment
import com.portal.ui.civilexam.CivilExamFragment
import com.portal.ui.cooking.CookingFragment
import com.portal.ui.couple.CoupleFragment
import com.portal.ui.crypto.CryptoFragment
import com.portal.ui.fashion.FashionFragment
import com.portal.ui.gnn.GnnFragment
import com.portal.ui.investment.InvestmentFragment
import com.portal.ui.manga.MangaFragment
import com.portal.ui.makeup.MakeupFragment
import com.portal.ui.music.MusicFragment
import com.portal.ui.recruitment.RecruitmentFragment
import com.portal.ui.settings.SettingsFragment
import com.portal.ui.studyabroad.StudyAbroadFragment
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class DashboardFragment : Fragment() {

    private var stats: DashboardStats? = null

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_dashboard, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val recyclerView = view.findViewById<RecyclerView>(R.id.rv_dashboard)
        recyclerView?.layoutManager = GridLayoutManager(requireContext(), 3)

        val swipeRefresh = view.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)
        swipeRefresh?.setOnRefreshListener { loadStats() }

        loadStats()
    }

    private fun loadStats() {
        view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = true
        GlobalScope.launch {
            try {
                PortalApp.instance.repository.getDashboardStats().observe(viewLifecycleOwner) { resource ->
                    view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            stats = resource.data
                            setupGrid()
                        }
                        is Resource.Error -> {
                            Snackbar.make(requireView(), "加载失败: ${resource.message}", Snackbar.LENGTH_SHORT).show()
                            setupGrid()
                        }
                        is Resource.Loading -> {}
                    }
                }
            } catch (e: Exception) {
                view?.post {
                    view?.findViewById<androidx.swiperefreshlayout.widget.SwipeRefreshLayout>(R.id.swipe_refresh)?.isRefreshing = false
                    setupGrid()
                }
            }
        }
    }

    private fun setupGrid() {
        val rv = view?.findViewById<RecyclerView>(R.id.rv_dashboard) ?: return
        val st = stats ?: DashboardStats()

        val modules = listOf(
            ModuleInfo("💕", "情侣空间", st.recruitmentQuestions.toString()) { CoupleFragment() },
            ModuleInfo("💼", "秋招备战", st.recruitmentQuestions.toString()) { RecruitmentFragment() },
            ModuleInfo("🔐", "密码学论文", st.cryptoPapers.toString()) { CryptoFragment() },
            ModuleInfo("🧠", "GNN匹配", "0") { GnnFragment() },
            ModuleInfo("📈", "投资理财", st.investmentRecords.toString()) { InvestmentFragment() },
            ModuleInfo("💄", "美妆系统", st.makeupTips.toString()) { MakeupFragment() },
            ModuleInfo("👗", "服装搭配", st.fashionItems.toString()) { FashionFragment() },
            ModuleInfo("🍳", "美食厨房", st.recipes.toString()) { CookingFragment() },
            ModuleInfo("✈️", "出国规划", st.studyAbroad.toString()) { StudyAbroadFragment() },
            ModuleInfo("📚", "考公备考", st.civilExamTopics.toString()) { CivilExamFragment() },
            ModuleInfo("📝", "CET考试", st.cetExamItems.toString()) { CetExamFragment() },
            ModuleInfo("🎭", "漫剧创作", st.mangaProjects.toString()) { MangaFragment() },
            ModuleInfo("⚙️", "系统设置", "") { SettingsFragment() }
        )

        rv.adapter = ModuleAdapter(modules) { fragment ->
            requireActivity().supportFragmentManager.beginTransaction()
                .replace(R.id.nav_host_fragment, fragment)
                .addToBackStack(null)
                .commit()
        }
    }

    data class ModuleInfo(val icon: String, val name: String, val count: String, val fragment: () -> Fragment)

    class ModuleAdapter(
        private val modules: List<ModuleInfo>,
        private val onClick: (Fragment) -> Unit
    ) : RecyclerView.Adapter<ModuleAdapter.VH>() {

        class VH(val card: MaterialCardView, val nameView: TextView, val countView: TextView) : RecyclerView.ViewHolder(card)

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val context = parent.context
            val card = MaterialCardView(context).apply {
                layoutParams = ViewGroup.MarginLayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, dp(context, 120)
                ).apply {
                    setMargins(dp(context, 4), dp(context, 4), dp(context, 4), dp(context, 4))
                }
                cardElevation = 2f
                radius = dp(context, 12).toFloat()
                setBackgroundColor(0xFFFFFFFF.toInt())
            }

            val nameView = TextView(context).apply {
                id = View.generateViewId()
                textAlignment = View.TEXT_ALIGNMENT_CENTER
                textSize = 11f
                setTextColor(0xFF333333.toInt())
            }

            val countView = TextView(context).apply {
                id = View.generateViewId()
                textAlignment = View.TEXT_ALIGNMENT_CENTER
                textSize = 13f
                setTypeface(null, android.graphics.Typeface.BOLD)
                setTextColor(0xFF673AB7.toInt())
            }

            val iconView = TextView(context).apply {
                id = View.generateViewId()
                textAlignment = View.TEXT_ALIGNMENT_CENTER
                textSize = 28f
            }

            val layout = android.widget.LinearLayout(context).apply {
                orientation = android.widget.LinearLayout.VERTICAL
                gravity = android.view.Gravity.CENTER
                val lp = android.widget.LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT
                )
                addView(iconView, lp)
                addView(nameView, lp)
                addView(countView, lp)
            }

            card.addView(layout)
            card.tag = iconView

            return VH(card, nameView, countView)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val module = modules[position]
            (holder.card.tag as? TextView)?.text = module.icon
            holder.nameView.text = module.name
            holder.countView.text = module.count
            holder.card.setOnClickListener { onClick(module.fragment()) }
        }

        override fun getItemCount() = modules.size

        private fun dp(context: android.content.Context, value: Int): Int {
            return (value * context.resources.displayMetrics.density).toInt()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
    }
}
