package com.portal.ui.manga

import android.app.AlertDialog
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.EditText
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.TextView
import androidx.fragment.app.Fragment
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
import com.portal.data.model.MangaCharacter
import com.portal.data.model.MangaProject
import com.portal.data.model.MangaScene
import com.portal.data.repository.Resource
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch

class MangaFragment : Fragment() {

    private lateinit var spinnerProject: Spinner
    private lateinit var tabManga: TabLayout
    private lateinit var viewPagerManga: androidx.viewpager2.widget.ViewPager2
    private lateinit var fabAddProject: FloatingActionButton
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var rootView: View

    private var projects = listOf<MangaProject>()
    private var currentProject: MangaProject? = null

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_manga, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        rootView = view
        spinnerProject = view.findViewById(R.id.spinner_project)
        tabManga = view.findViewById(R.id.tab_manga)
        viewPagerManga = view.findViewById(R.id.view_pager_manga)
        fabAddProject = view.findViewById(R.id.fab_add_project)
        swipeRefresh = view.findViewById(R.id.swipe_refresh)

        // Setup ViewPager with Scenes/Characters tabs
        val pagerAdapter = MangaPagerAdapter(this)
        viewPagerManga.adapter = pagerAdapter

        TabLayoutMediator(tabManga, viewPagerManga) { tab, position ->
            tab.text = if (position == 0) "Scenes" else "Characters"
        }.attach()

        // Project selector spinner
        spinnerProject.onItemSelectedListener =
            object : android.widget.AdapterView.OnItemSelectedListener {
                override fun onItemSelected(
                    parent: android.widget.AdapterView<*>?,
                    view: View?,
                    position: Int,
                    id: Long
                ) {
                    if (position in projects.indices) {
                        currentProject = projects[position]
                    }
                }

                override fun onNothingSelected(parent: android.widget.AdapterView<*>?) {}
            }

        // FAB - create new project
        fabAddProject.setOnClickListener {
            showCreateProjectDialog()
        }

        // Swipe refresh
        swipeRefresh.setOnRefreshListener {
            loadProjects()
        }

        loadProjects()
    }

    private fun loadProjects() {
        swipeRefresh.isRefreshing = true
        PortalApp.instance.repository.getMangaProjects()
            .observe(viewLifecycleOwner) { resource ->
                when (resource) {
                    is Resource.Success -> {
                        projects = resource.data
                        swipeRefresh.isRefreshing = false

                        val adapter = ArrayAdapter(
                            requireContext(),
                            android.R.layout.simple_spinner_item,
                            projects.map { it.title }
                        ).apply {
                            setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
                        }
                        spinnerProject.adapter = adapter

                        if (projects.isNotEmpty() && currentProject == null) {
                            currentProject = projects[0]
                        }
                    }
                    is Resource.Error -> {
                        swipeRefresh.isRefreshing = false
                        Snackbar.make(
                            rootView,
                            resource.message,
                            Snackbar.LENGTH_SHORT
                        ).show()
                    }
                    is Resource.Loading -> {
                        swipeRefresh.isRefreshing = true
                    }
                }
            }
    }

    private fun showCreateProjectDialog() {
        val context = requireContext()
        val layout = LinearLayout(context).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(48, 24, 48, 0)
        }

        val etTitle = EditText(context).apply { hint = "Project Title" }
        val etDescription = EditText(context).apply { hint = "Description" }
        val etNovelText = EditText(context).apply {
            hint = "Novel Text / Script"
            minLines = 3
        }
        val etStyle = EditText(context).apply {
            hint = "Style (e.g. anime, manga, realistic)"
            setText("anime")
        }

        layout.addView(etTitle)
        layout.addView(etDescription)
        layout.addView(etNovelText)
        layout.addView(etStyle)

        AlertDialog.Builder(context)
            .setTitle("Create New Manga Project")
            .setView(layout)
            .setPositiveButton("Create") { _, _ ->
                val title = etTitle.text.toString().trim()
                val description = etDescription.text.toString().trim()
                val novelText = etNovelText.text.toString().trim()
                val style = etStyle.text.toString().trim().ifEmpty { "anime" }

                if (title.isNotEmpty()) {
                    GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
                        try {
                            PortalApp.instance.repository.createMangaProject(
                                title, description, novelText, style
                            )
                            Snackbar.make(
                                rootView,
                                "Project created!",
                                Snackbar.LENGTH_SHORT
                            ).show()
                            loadProjects()
                        } catch (e: Exception) {
                            Snackbar.make(
                                rootView,
                                e.message ?: "Failed to create project",
                                Snackbar.LENGTH_SHORT
                            ).show()
                        }
                    }
                } else {
                    Snackbar.make(
                        rootView,
                        "Title is required",
                        Snackbar.LENGTH_SHORT
                    ).show()
                }
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    // ========== ViewPager Adapter ==========

    inner class MangaPagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
        override fun getItemCount(): Int = 2

        override fun createFragment(position: Int): Fragment {
            return if (position == 0) {
                MangaSceneFragment()
            } else {
                MangaCharacterFragment()
            }
        }
    }
}

// ========== Scene Tab Fragment ==========

class MangaSceneFragment : Fragment() {

    private var recyclerView: RecyclerView? = null
    private var swipeRefresh: SwipeRefreshLayout? = null
    private var rootView: View? = null
    private val scenes = mutableListOf<MangaScene>()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
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

        val adapter = MangaSceneAdapter(
            onGenerateImage = { scene -> generateSceneImage(scene) },
            onGenerateVideo = { scene -> generateSceneVideo(scene) }
        )
        recyclerView?.layoutManager = LinearLayoutManager(requireContext())
        recyclerView?.adapter = adapter

        swipeRefresh?.setOnRefreshListener {
            loadScenes()
        }

        loadScenes()
    }

    private fun loadScenes() {
        swipeRefresh?.isRefreshing = true
        PortalApp.instance.repository.getMangaScenes("")
            .observe(viewLifecycleOwner) { resource ->
                swipeRefresh?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        scenes.clear()
                        scenes.addAll(resource.data.scenes)
                        (recyclerView?.adapter as? MangaSceneAdapter)?.submitList(scenes.toList())
                    }
                    is Resource.Error -> {
                        Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                    is Resource.Loading -> {}
                }
            }
    }

    private fun generateSceneImage(scene: MangaScene) {
        GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
            try {
                Snackbar.make(
                    rootView!!,
                    "Generating image for scene ${scene.sceneNumber}...",
                    Snackbar.LENGTH_SHORT
                ).show()
                PortalApp.instance.repository.generateSceneImage(scene.id)
                    .observe(viewLifecycleOwner) { resource ->
                        when (resource) {
                            is Resource.Success -> {
                                Snackbar.make(
                                    rootView!!,
                                    "Image generated!",
                                    Snackbar.LENGTH_SHORT
                                ).show()
                                loadScenes()
                            }
                            is Resource.Error -> {
                                Snackbar.make(
                                    rootView!!,
                                    "Image generation failed: ${resource.message}",
                                    Snackbar.LENGTH_SHORT
                                ).show()
                            }
                            is Resource.Loading -> {}
                        }
                    }
            } catch (e: Exception) {
                Snackbar.make(
                    rootView!!,
                    e.message ?: "Error generating image",
                    Snackbar.LENGTH_SHORT
                ).show()
            }
        }
    }

    private fun generateSceneVideo(scene: MangaScene) {
        GlobalScope.launch(kotlinx.coroutines.Dispatchers.Main) {
            try {
                Snackbar.make(
                    rootView!!,
                    "Generating video for scene ${scene.sceneNumber}...",
                    Snackbar.LENGTH_SHORT
                ).show()
                PortalApp.instance.repository.generateSceneVideo(scene.id)
                    .observe(viewLifecycleOwner) { resource ->
                        when (resource) {
                            is Resource.Success -> {
                                Snackbar.make(
                                    rootView!!,
                                    "Video generation started!",
                                    Snackbar.LENGTH_SHORT
                                ).show()
                                loadScenes()
                            }
                            is Resource.Error -> {
                                Snackbar.make(
                                    rootView!!,
                                    "Video generation failed: ${resource.message}",
                                    Snackbar.LENGTH_SHORT
                                ).show()
                            }
                            is Resource.Loading -> {}
                        }
                    }
            } catch (e: Exception) {
                Snackbar.make(
                    rootView!!,
                    e.message ?: "Error generating video",
                    Snackbar.LENGTH_SHORT
                ).show()
            }
        }
    }
}

// ========== Character Tab Fragment ==========

class MangaCharacterFragment : Fragment() {

    private var recyclerView: RecyclerView? = null
    private var swipeRefresh: SwipeRefreshLayout? = null
    private var rootView: View? = null
    private val characters = mutableListOf<MangaCharacter>()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
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

        recyclerView?.layoutManager = LinearLayoutManager(requireContext())
        recyclerView?.adapter = MangaCharacterAdapter()

        swipeRefresh?.setOnRefreshListener {
            loadCharacters()
        }

        loadCharacters()
    }

    private fun loadCharacters() {
        swipeRefresh?.isRefreshing = true
        PortalApp.instance.repository.getMangaScenes("")
            .observe(viewLifecycleOwner) { resource ->
                swipeRefresh?.isRefreshing = false
                when (resource) {
                    is Resource.Success -> {
                        // Characters come from the MangaScenesResponse but our
                        // getMangaScenes returns List<MangaScene>. For now we
                        // show an empty list; characters can be loaded via
                        // a dedicated endpoint when available.
                    }
                    is Resource.Error -> {
                        Snackbar.make(rootView!!, resource.message, Snackbar.LENGTH_SHORT).show()
                    }
                    is Resource.Loading -> {}
                }
            }
    }
}

// ========== Scene Adapter ==========

class MangaSceneAdapter(
    private val onGenerateImage: (MangaScene) -> Unit,
    private val onGenerateVideo: (MangaScene) -> Unit
) : RecyclerView.Adapter<MangaSceneAdapter.SceneVH>() {

    private var items = listOf<MangaScene>()

    fun submitList(list: List<MangaScene>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): SceneVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_manga_scene, parent, false)
        return SceneVH(view)
    }

    override fun onBindViewHolder(holder: SceneVH, position: Int) {
        val item = items[position]

        holder.tvSceneNumber.text = "Scene ${item.sceneNumber}"
        holder.tvTitle.text = item.title
        holder.tvDescription.text = item.description
        holder.chipStatus.text = item.status

        // Load thumbnail with Glide
        if (!item.imageUrl.isNullOrEmpty()) {
            Glide.with(holder.ivThumbnail)
                .load(item.imageUrl)
                .centerCrop()
                .placeholder(android.R.drawable.ic_menu_gallery)
                .into(holder.ivThumbnail)
            holder.ivThumbnail.visibility = View.VISIBLE
        } else {
            holder.ivThumbnail.setImageResource(android.R.drawable.ic_menu_gallery)
            holder.ivThumbnail.visibility = View.VISIBLE
        }

        // Generate Image button
        holder.btnGenImage.setOnClickListener {
            onGenerateImage(item)
        }

        // Generate Video button
        holder.btnGenVideo.setOnClickListener {
            onGenerateVideo(item)
        }
    }

    override fun getItemCount() = items.size

    class SceneVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvSceneNumber: TextView = view.findViewById(R.id.tv_scene_number)
        val tvTitle: TextView = view.findViewById(R.id.tv_title)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
        val chipStatus: com.google.android.material.chip.Chip = view.findViewById(R.id.chip_status)
        val ivThumbnail: ImageView = view.findViewById(R.id.iv_thumbnail)
        val btnGenImage: com.google.android.material.button.MaterialButton = view.findViewById(R.id.btn_gen_image)
        val btnGenVideo: com.google.android.material.button.MaterialButton = view.findViewById(R.id.btn_gen_video)
    }
}

// ========== Character Adapter ==========

class MangaCharacterAdapter : RecyclerView.Adapter<MangaCharacterAdapter.CharVH>() {

    private var items = listOf<MangaCharacter>()

    fun submitList(list: List<MangaCharacter>) {
        items = list
        notifyDataSetChanged()
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CharVH {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_manga_character, parent, false)
        return CharVH(view)
    }

    override fun onBindViewHolder(holder: CharVH, position: Int) {
        val item = items[position]
        holder.tvName.text = item.name
        holder.tvDescription.text = item.description
        holder.tvAppearance.text = item.appearance
        holder.tvPersonality.text = item.personality

        if (!item.referenceUrl.isNullOrEmpty()) {
            // Glide.with(holder.ivReference)
            //     .load(item.referenceUrl)
            //     .centerCrop()
            //     .placeholder(android.R.drawable.ic_menu_gallery)
            //     .into(holder.ivReference)
        }
    }

    override fun getItemCount() = items.size

    class CharVH(view: View) : RecyclerView.ViewHolder(view) {
        val tvName: TextView = view.findViewById(R.id.tv_name)
        val tvDescription: TextView = view.findViewById(R.id.tv_description)
        val tvAppearance: TextView = view.findViewById(R.id.tv_appearance)
        val tvPersonality: TextView = view.findViewById(R.id.tv_personality)
    }
}
