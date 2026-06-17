package com.portal.ui.study

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.portal.R
import com.portal.ui.cetexam.CetExamFragment
import com.portal.ui.civilexam.CivilExamFragment
import com.portal.ui.crypto.CryptoFragment
import com.portal.ui.gnn.GnnFragment
import com.portal.ui.recruitment.RecruitmentFragment

class StudyFragment : Fragment() {

    private val tabTitles = listOf("秋招", "密码学", "GNN", "考公", "CET")

    override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View? {
        return inflater.inflate(R.layout.fragment_study, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val tabLayout = view.findViewById<TabLayout>(R.id.tab_study)
        val viewPager = view.findViewById<androidx.viewpager2.widget.ViewPager2>(R.id.view_pager_study)

        if (viewPager != null && tabLayout != null) {
            viewPager.adapter = object : FragmentStateAdapter(this) {
                override fun getItemCount() = 5
                override fun createFragment(position: Int): Fragment {
                    return when (position) {
                        0 -> RecruitmentFragment()
                        1 -> CryptoFragment()
                        2 -> GnnFragment()
                        3 -> CivilExamFragment()
                        4 -> CetExamFragment()
                        else -> RecruitmentFragment()
                    }
                }
            }
            TabLayoutMediator(tabLayout, viewPager) { tab, pos -> tab.text = tabTitles[pos] }.attach()
        }
    }
}
