package com.portal.ui.recruitment

import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.GithubRepo
import com.portal.data.model.RecruitmentQuestion
import com.portal.data.model.RecruitmentQuestionsResponse
import com.portal.data.model.YoutubeResource
import com.portal.data.repository.Resource

class RecruitmentFragment : Fragment() {

    private var rootView: View? = null

    private val tabLayout: TabLayout
        get() = rootView!!.findViewById(R.id.tab_recruitment)
    private val viewPager: androidx.viewpager2.widget.ViewPager2
        get() = rootView!!.findViewById(R.id.view_pager_recruitment)

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val view = inflater.inflate(R.layout.fragment_recruitment, container, false)
        rootView = view
        return view
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val adapter = RecruitmentPagerAdapter(this)
        viewPager.adapter = adapter

        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "LeetCode"
                1 -> "GitHub"
                2 -> "YouTube"
                else -> ""
            }
        }.attach()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        rootView = null
    }

    private class RecruitmentPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
        override fun getItemCount(): Int = 3
        override fun createFragment(position: Int): Fragment {
            return RecruitmentTabFragment.newInstance(position)
        }
    }
}

// ========== Tab Fragment ==========

class RecruitmentTabFragment : Fragment() {

    companion object {
        private const val ARG_TAB = "tab"

        fun newInstance(tab: Int) = RecruitmentTabFragment().apply {
            arguments = Bundle().apply { putInt(ARG_TAB, tab) }
        }
    }

    private var tabIndex: Int = 0
    private var rootView: View? = null
    private var recyclerView: RecyclerView? = null
    private var swipeRefresh: SwipeRefreshLayout? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        tabIndex = arguments?.getInt(ARG_TAB, 0) ?: 0
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_recruitment_tab, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        rootView = view

        swipeRefresh = view as SwipeRefreshLayout
        recyclerView = view.findViewById(R.id.rv_tab_content)
        recyclerView!!.layoutManager = LinearLayoutManager(requireContext())

        swipeRefresh!!.setOnRefreshListener { loadData() }
        loadData()
    }

    private fun loadData() {
        swipeRefresh?.isRefreshing = true
        when (tabIndex) {
            0 -> loadQuestions()
            1 -> loadRepos()
            2 -> loadYoutube()
        }
    }

    private fun loadQuestions() {
        PortalApp.instance.repository.getRecruitmentQuestions()
            .observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        swipeRefresh?.isRefreshing = false
                        val response = resource.data as RecruitmentQuestionsResponse
                        val adapter = QuestionAdapter()
                        adapter.submitList(response.questions)
                        recyclerView?.adapter = adapter
                    }
                    is Resource.Error -> {
                        swipeRefresh?.isRefreshing = false
                        Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                    is Resource.Loading -> {
                        swipeRefresh?.isRefreshing = true
                    }
                }
            }
    }

    private fun loadRepos() {
        PortalApp.instance.repository.getRecruitmentRepos()
            .observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        swipeRefresh?.isRefreshing = false
                        @Suppress("UNCHECKED_CAST")
                        val repos = resource.data as List<GithubRepo>
                        val adapter = RepoAdapter()
                        adapter.submitList(repos)
                        recyclerView?.adapter = adapter
                    }
                    is Resource.Error -> {
                        swipeRefresh?.isRefreshing = false
                        Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                    is Resource.Loading -> {
                        swipeRefresh?.isRefreshing = true
                    }
                }
            }
    }

    private fun loadYoutube() {
        PortalApp.instance.repository.getRecruitmentYoutube()
            .observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        swipeRefresh?.isRefreshing = false
                        @Suppress("UNCHECKED_CAST")
                        val videos = resource.data as List<YoutubeResource>
                        val adapter = YoutubeAdapter()
                        adapter.submitList(videos)
                        recyclerView?.adapter = adapter
                    }
                    is Resource.Error -> {
                        swipeRefresh?.isRefreshing = false
                        Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                    is Resource.Loading -> {
                        swipeRefresh?.isRefreshing = true
                    }
                }
            }
    }
}

// ========== Adapters ==========

class QuestionAdapter : RecyclerView.Adapter<QuestionAdapter.QVH>() {

    private var items = listOf<RecruitmentQuestion>()

    fun submitList(list: List<RecruitmentQuestion>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): QVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_question, parent, false)
        return QVH(view)
    }

    override fun onBindViewHolder(holder: QVH, position: Int) {
        val item = items[position]
        holder.tvTitle.text = item.title
        holder.chipDifficulty.text = item.difficulty
        holder.chipCategory.text = item.category
        holder.tvDescription.text = item.description

        // Color-code difficulty chip
        val bgColor = when (item.difficulty.lowercase()) {
            "easy" -> Color.parseColor("#4CAF50")
            "medium" -> Color.parseColor("#FF9800")
            "hard" -> Color.parseColor("#F44336")
            else -> Color.parseColor("#9E9E9E")
        }
        val drawable = GradientDrawable().apply {
            setColor(bgColor)
            cornerRadius = 16f
        }
        holder.chipDifficulty.background = drawable
        holder.chipDifficulty.setTextColor(Color.WHITE)

        // Category chip color
        val catBg = GradientDrawable().apply {
            setColor(Color.parseColor("#E3F2FD"))
            cornerRadius = 16f
        }
        holder.chipCategory.background = catBg
        holder.chipCategory.setTextColor(Color.parseColor("#1565C0"))
    }

    override fun getItemCount() = items.size

    class QVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tv_title)
        val chipDifficulty: TextView = view.findViewById(R.id.chip_difficulty)
        val chipCategory: TextView = view.findViewById(R.id.chip_category)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
    }
}

class RepoAdapter : RecyclerView.Adapter<RepoAdapter.RepoVH>() {

    private var items = listOf<GithubRepo>()

    fun submitList(list: List<GithubRepo>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): RepoVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_repo, parent, false)
        return RepoVH(view)
    }

    override fun onBindViewHolder(holder: RepoVH, position: Int) {
        val item = items[position]
        holder.tvName.text = item.name
        holder.tvStars.text = "\u2605 ${item.stars}"
        holder.chipLanguage.text = item.language
        holder.tvDescription.text = item.description

        // Color-code language chip
        val langColor = languageColor(item.language)
        val drawable = GradientDrawable().apply {
            setColor(langColor)
            cornerRadius = 16f
        }
        holder.chipLanguage.background = drawable
        holder.chipLanguage.setTextColor(Color.WHITE)
    }

    override fun getItemCount() = items.size

    private fun languageColor(language: String): Int {
        return when (language.lowercase()) {
            "python" -> Color.parseColor("#3776AB")
            "javascript" -> Color.parseColor("#B8860B")
            "java" -> Color.parseColor("#ED8B00")
            "kotlin" -> Color.parseColor("#7F52FF")
            "go" -> Color.parseColor("#00ADD8")
            "rust" -> Color.parseColor("#8B4513")
            "c++" -> Color.parseColor("#00599C")
            "typescript" -> Color.parseColor("#3178C6")
            else -> Color.parseColor("#8E8E93")
        }
    }

    class RepoVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tv_name)
        val tvStars: TextView = view.findViewById(R.id.tv_stars)
        val chipLanguage: TextView = view.findViewById(R.id.chip_language)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
    }
}

class YoutubeAdapter : RecyclerView.Adapter<YoutubeAdapter.YVH>() {

    private var items = listOf<YoutubeResource>()

    fun submitList(list: List<YoutubeResource>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): YVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_youtube, parent, false)
        return YVH(view)
    }

    override fun onBindViewHolder(holder: YVH, position: Int) {
        val item = items[position]
        holder.tvTitle.text = item.title
        holder.chipChannel.text = item.channel
        holder.tvDescription.text = item.description
    }

    override fun getItemCount() = items.size

    class YVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvTitle: TextView = view.findViewById(R.id.tv_title)
        val chipChannel: TextView = view.findViewById(R.id.chip_channel)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
    }
}
