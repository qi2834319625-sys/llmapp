package com.portal.ui.couple

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.EditText
import android.widget.ImageView
import android.widget.TextView
import androidx.fragment.app.Fragment
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import androidx.viewpager2.adapter.FragmentStateAdapter
import com.bumptech.glide.Glide
import com.google.android.material.floatingactionbutton.FloatingActionButton
import com.google.android.material.snackbar.Snackbar
import com.google.android.material.tabs.TabLayout
import com.google.android.material.tabs.TabLayoutMediator
import com.portal.PortalApp
import com.portal.R
import com.portal.data.model.CoupleBucketItem
import com.portal.data.model.CoupleLetter
import com.portal.data.model.CouplePhoto
import com.portal.data.model.CoupleStory
import com.portal.data.model.CoupleTimeline
import com.portal.data.model.CoupleVideo
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class CoupleFragment : Fragment() {

    private val tabTitles = listOf("故事", "时间线", "照片", "视频", "情书", "心愿单")

    private lateinit var tabCouple: TabLayout
    private lateinit var viewPagerCouple: androidx.viewpager2.widget.ViewPager2
    private lateinit var fabAdd: FloatingActionButton

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_couple, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        tabCouple = view.findViewById(R.id.tab_couple)
        viewPagerCouple = view.findViewById(R.id.view_pager_couple)
        fabAdd = view.findViewById(R.id.fab_add)

        val adapter = CoupleTabAdapter(this)
        viewPagerCouple.adapter = adapter

        TabLayoutMediator(tabCouple, viewPagerCouple) { tab, position ->
            tab.text = tabTitles[position]
        }.attach()

        fabAdd.setOnClickListener {
            val currentTab = tabCouple.selectedTabPosition
            showAddDialog(currentTab)
        }
    }

    private fun showAddDialog(tabIndex: Int) {
        val context = requireContext()
        when (tabIndex) {
            0 -> { // 故事
                val layout = android.widget.LinearLayout(context).apply {
                    orientation = android.widget.LinearLayout.VERTICAL
                    setPadding(48, 24, 48, 0)
                }
                val etTitle = EditText(context).apply { hint = "故事标题" }
                val etContent = EditText(context).apply { hint = "故事内容" }
                layout.addView(etTitle)
                layout.addView(etContent)
                AlertDialog.Builder(context)
                    .setTitle("新建故事")
                    .setView(layout)
                    .setPositiveButton("添加") { _, _ ->
                        val title = etTitle.text.toString().trim()
                        val content = etContent.text.toString().trim()
                        if (title.isNotEmpty() && content.isNotEmpty()) {
                            GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                                try {
                                    PortalApp.instance.repository.addCoupleStory(title, content)
                                    Snackbar.make(requireView(), "故事已添加", Snackbar.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Snackbar.make(requireView(), e.message ?: "添加失败", Snackbar.LENGTH_SHORT).show()
                                }
                            }
                        }
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
            1 -> { // 时间线
                val layout = android.widget.LinearLayout(context).apply {
                    orientation = android.widget.LinearLayout.VERTICAL
                    setPadding(48, 24, 48, 0)
                }
                val etDate = EditText(context).apply { hint = "日期 (YYYY-MM-DD)" }
                val etTitle = EditText(context).apply { hint = "事件标题" }
                val etDesc = EditText(context).apply { hint = "描述" }
                layout.addView(etDate)
                layout.addView(etTitle)
                layout.addView(etDesc)
                AlertDialog.Builder(context)
                    .setTitle("添加时间线事件")
                    .setView(layout)
                    .setPositiveButton("添加") { _, _ ->
                        val date = etDate.text.toString().trim()
                        val title = etTitle.text.toString().trim()
                        val desc = etDesc.text.toString().trim()
                        if (date.isNotEmpty() && title.isNotEmpty()) {
                            GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                                try {
                                    PortalApp.instance.repository.addCoupleTimeline(date, title, desc)
                                    Snackbar.make(requireView(), "事件已添加", Snackbar.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Snackbar.make(requireView(), e.message ?: "添加失败", Snackbar.LENGTH_SHORT).show()
                                }
                            }
                        }
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
            2 -> { // 照片
                Snackbar.make(requireView(), "请上传照片", Snackbar.LENGTH_SHORT).show()
            }
            3 -> { // 视频
                Snackbar.make(requireView(), "请上传视频", Snackbar.LENGTH_SHORT).show()
            }
            4 -> { // 情书
                val layout = android.widget.LinearLayout(context).apply {
                    orientation = android.widget.LinearLayout.VERTICAL
                    setPadding(48, 24, 48, 0)
                }
                val etSender = EditText(context).apply { hint = "署名" }
                val etTitle = EditText(context).apply { hint = "标题" }
                val etContent = EditText(context).apply { hint = "情书内容" }
                layout.addView(etSender)
                layout.addView(etTitle)
                layout.addView(etContent)
                AlertDialog.Builder(context)
                    .setTitle("写情书")
                    .setView(layout)
                    .setPositiveButton("发送") { _, _ ->
                        val sender = etSender.text.toString().trim()
                        val title = etTitle.text.toString().trim()
                        val content = etContent.text.toString().trim()
                        if (sender.isNotEmpty() && title.isNotEmpty() && content.isNotEmpty()) {
                            GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                                try {
                                    PortalApp.instance.repository.addCoupleLetter(sender, title, content)
                                    Snackbar.make(requireView(), "情书已发送", Snackbar.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Snackbar.make(requireView(), e.message ?: "发送失败", Snackbar.LENGTH_SHORT).show()
                                }
                            }
                        }
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
            5 -> { // 心愿单
                val layout = android.widget.LinearLayout(context).apply {
                    orientation = android.widget.LinearLayout.VERTICAL
                    setPadding(48, 24, 48, 0)
                }
                val etItem = EditText(context).apply { hint = "心愿内容" }
                layout.addView(etItem)
                AlertDialog.Builder(context)
                    .setTitle("添加心愿")
                    .setView(layout)
                    .setPositiveButton("添加") { _, _ ->
                        val item = etItem.text.toString().trim()
                        if (item.isNotEmpty()) {
                            GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                                try {
                                    PortalApp.instance.repository.addCoupleBucket(item)
                                    Snackbar.make(requireView(), "心愿已添加", Snackbar.LENGTH_SHORT).show()
                                } catch (e: Exception) {
                                    Snackbar.make(requireView(), e.message ?: "添加失败", Snackbar.LENGTH_SHORT).show()
                                }
                            }
                        }
                    }
                    .setNegativeButton("取消", null)
                    .show()
            }
        }
    }

    // ========== ViewPager Adapter ==========

    inner class CoupleTabAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
        override fun getItemCount(): Int = 6

        override fun createFragment(position: Int): Fragment {
            val type = when (position) {
                0 -> CouplePagerFragment.TYPE_STORIES
                1 -> CouplePagerFragment.TYPE_TIMELINE
                2 -> CouplePagerFragment.TYPE_PHOTOS
                3 -> CouplePagerFragment.TYPE_VIDEOS
                4 -> CouplePagerFragment.TYPE_LETTERS
                5 -> CouplePagerFragment.TYPE_BUCKET
                else -> CouplePagerFragment.TYPE_STORIES
            }
            return CouplePagerFragment.newInstance(type)
        }
    }
}

// ========== Child Fragments for each tab ==========

class CouplePagerFragment : Fragment() {

    companion object {
        const val ARG_TYPE = "tab_type"
        const val TYPE_STORIES = 0
        const val TYPE_TIMELINE = 1
        const val TYPE_PHOTOS = 2
        const val TYPE_VIDEOS = 3
        const val TYPE_LETTERS = 4
        const val TYPE_BUCKET = 5

        fun newInstance(type: Int): CouplePagerFragment {
            return CouplePagerFragment().apply {
                arguments = Bundle().apply { putInt(ARG_TYPE, type) }
            }
        }
    }

    private var swipeRefresh: SwipeRefreshLayout? = null
    private var recyclerView: RecyclerView? = null
    private var rootView: View? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Build SwipeRefreshLayout + RecyclerView programmatically
        val ctx = requireContext()
        val srl = SwipeRefreshLayout(ctx)
        val rv = RecyclerView(ctx)
        rv.layoutParams = ViewGroup.LayoutParams(
            ViewGroup.LayoutParams.MATCH_PARENT,
            ViewGroup.LayoutParams.MATCH_PARENT
        )
        srl.addView(rv)
        swipeRefresh = srl
        recyclerView = rv
        rootView = srl
        return srl
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        val tabType = arguments?.getInt(ARG_TYPE) ?: 0

        setupRecyclerView(tabType)
        loadData(tabType)
    }

    private fun setupRecyclerView(tabType: Int) {
        val rv = recyclerView ?: return
        when (tabType) {
            TYPE_PHOTOS -> {
                rv.layoutManager = GridLayoutManager(requireContext(), 3)
                rv.adapter = CouplePhotoAdapter()
            }
            TYPE_VIDEOS -> {
                rv.layoutManager = GridLayoutManager(requireContext(), 3)
                rv.adapter = CoupleVideoAdapter()
            }
            TYPE_STORIES -> {
                rv.layoutManager = LinearLayoutManager(requireContext())
                rv.adapter = CoupleStoryAdapter()
            }
            TYPE_TIMELINE -> {
                rv.layoutManager = LinearLayoutManager(requireContext())
                rv.adapter = CoupleTimelineAdapter()
            }
            TYPE_LETTERS -> {
                rv.layoutManager = LinearLayoutManager(requireContext())
                rv.adapter = CoupleLetterAdapter()
            }
            TYPE_BUCKET -> {
                rv.layoutManager = LinearLayoutManager(requireContext())
                rv.adapter = CoupleBucketAdapter()
            }
        }

        swipeRefresh?.setOnRefreshListener {
            loadData(tabType)
        }
    }

    @Suppress("UNCHECKED_CAST")
    private fun loadData(tabType: Int) {
        swipeRefresh?.isRefreshing = true

        when (tabType) {
            TYPE_PHOTOS -> {
                PortalApp.instance.repository.getCouplePhotos().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CouplePhotoAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
            TYPE_VIDEOS -> {
                PortalApp.instance.repository.getCoupleVideos().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CoupleVideoAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
            TYPE_STORIES -> {
                PortalApp.instance.repository.getCoupleStories().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CoupleStoryAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
            TYPE_TIMELINE -> {
                PortalApp.instance.repository.getCoupleTimeline().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CoupleTimelineAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
            TYPE_LETTERS -> {
                PortalApp.instance.repository.getCoupleLetters().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CoupleLetterAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
            TYPE_BUCKET -> {
                PortalApp.instance.repository.getCoupleBucketlist().observe(viewLifecycleOwner) { resource ->
                    swipeRefresh?.isRefreshing = false
                    when (resource) {
                        is Resource.Success -> {
                            (recyclerView?.adapter as? CoupleBucketAdapter)?.submitList(resource.data)
                        }
                        is Resource.Error -> {
                            Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                        }
                        is Resource.Loading -> {}
                    }
                }
            }
        }
    }

    // ========== Adapters ==========

    class CouplePhotoAdapter : RecyclerView.Adapter<CouplePhotoAdapter.VH>() {
        private var items = listOf<CouplePhoto>()

        fun submitList(list: List<CouplePhoto>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val iv = ImageView(parent.context).apply {
                layoutParams = ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    300
                )
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            return VH(iv)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            Glide.with(holder.iv)
                .load(item.filename)
                .centerCrop()
                .into(holder.iv)
        }

        override fun getItemCount() = items.size
        class VH(val iv: ImageView) : RecyclerView.ViewHolder(iv)
    }

    class CoupleVideoAdapter : RecyclerView.Adapter<CoupleVideoAdapter.VH>() {
        private var items = listOf<CoupleVideo>()

        fun submitList(list: List<CoupleVideo>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val iv = ImageView(parent.context).apply {
                layoutParams = ViewGroup.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT,
                    300
                )
                scaleType = ImageView.ScaleType.CENTER_CROP
            }
            return VH(iv)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            Glide.with(holder.iv)
                .load(item.filename)
                .centerCrop()
                .into(holder.iv)
        }

        override fun getItemCount() = items.size
        class VH(val iv: ImageView) : RecyclerView.ViewHolder(iv)
    }

    class CoupleStoryAdapter : RecyclerView.Adapter<CoupleStoryAdapter.VH>() {
        private var items = listOf<CoupleStory>()

        fun submitList(list: List<CoupleStory>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_couple_story, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.tvTitle.text = item.title
            holder.tvContent.text = item.content
            holder.tvMood.text = item.mood
        }

        override fun getItemCount() = items.size
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val tvTitle: TextView = view.findViewById(R.id.tv_title)
            val tvContent: TextView = view.findViewById(R.id.tv_content)
            val tvMood: TextView = view.findViewById(R.id.tv_mood)
        }
    }

    class CoupleTimelineAdapter : RecyclerView.Adapter<CoupleTimelineAdapter.VH>() {
        private var items = listOf<CoupleTimeline>()

        fun submitList(list: List<CoupleTimeline>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_couple_timeline, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.tvTitle.text = item.title
            holder.tvDate.text = item.eventDate
            holder.tvDescription.text = item.description
        }

        override fun getItemCount() = items.size
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val tvTitle: TextView = view.findViewById(R.id.tv_title)
            val tvDate: TextView = view.findViewById(R.id.tv_date)
            val tvDescription: TextView = view.findViewById(R.id.tv_description)
        }
    }

    class CoupleLetterAdapter : RecyclerView.Adapter<CoupleLetterAdapter.VH>() {
        private var items = listOf<CoupleLetter>()

        fun submitList(list: List<CoupleLetter>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_couple_letter, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.tvTitle.text = item.title
            holder.tvSender.text = item.sender
        }

        override fun getItemCount() = items.size
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val tvTitle: TextView = view.findViewById(R.id.tv_title)
            val tvSender: TextView = view.findViewById(R.id.tv_sender)
        }
    }

    class CoupleBucketAdapter : RecyclerView.Adapter<CoupleBucketAdapter.VH>() {
        private var items = listOf<CoupleBucketItem>()

        fun submitList(list: List<CoupleBucketItem>) {
            items = list
            notifyDataSetChanged()
        }

        override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VH {
            val view = LayoutInflater.from(parent.context)
                .inflate(R.layout.item_couple_bucket, parent, false)
            return VH(view)
        }

        override fun onBindViewHolder(holder: VH, position: Int) {
            val item = items[position]
            holder.tvTitle.text = item.item
            holder.tvCategory.text = item.category
            holder.tvDone.text = if (item.isDone != 0) "已完成" else "未完成"
        }

        override fun getItemCount() = items.size
        class VH(view: View) : RecyclerView.ViewHolder(view) {
            val tvTitle: TextView = view.findViewById(R.id.tv_item)
            val tvCategory: TextView = view.findViewById(R.id.tv_category)
            val tvDone: TextView = view.findViewById(R.id.cb_done)
        }
    }
}
