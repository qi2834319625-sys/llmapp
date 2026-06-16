"""
Seed data for all modules.
Each function seeds one module; called from init_db().
"""
import sqlite3

from seed_cet import seed_cet_exam
from seed_manga import seed_manga

def seed_all_data(conn: sqlite3.Connection):
    seed_recruitment(conn)
    seed_github(conn)
    seed_youtube(conn)
    seed_crypto(conn)
    seed_gnn(conn)
    seed_investment(conn)
    seed_makeup(conn)
    seed_fashion(conn)
    seed_cooking(conn)
    seed_study_abroad(conn)
    seed_civil_exam(conn)
    seed_cet_exam(conn)
    seed_manga(conn)
    seed_couple_stories(conn)


def seed_recruitment(conn):
    if conn.execute("SELECT COUNT(*) FROM recruitment_questions").fetchone()[0] >= 100:
        return
    qs = [
        ("Two Sum","Easy","Array","Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.","Use a hash map to store complement values. For each num, check if target - num exists in map. Time: O(n), Space: O(n). Community: two-pointer after sorting also works.","https://leetcode.com/problems/two-sum/","LeetCode Hot 100"),
        ("Add Two Numbers","Medium","Linked List","You are given two non-empty linked lists representing two non-negative integers. Add them and return as linked list.","Traverse both lists simultaneously, track carry. Create new nodes for result. Handle different lengths and final carry. Community: recursive solution is cleaner.","https://leetcode.com/problems/add-two-numbers/","LeetCode Hot 100"),
        ("Longest Substring Without Repeating Characters","Medium","String","Given a string s, find the length of the longest substring without repeating characters.","Sliding window with hash set. Expand right, shrink left when duplicate found. Track max length. Community: array instead of HashSet is faster.","https://leetcode.com/problems/longest-substring-without-repeating-characters/","LeetCode Hot 100"),
        ("Median of Two Sorted Arrays","Hard","Array","Given two sorted arrays nums1 and nums2, return the median of the two sorted arrays.","Binary search on smaller array. Partition both arrays such that left half has same elements as right half. O(log(min(m,n))). Community: understanding partition is key.","https://leetcode.com/problems/median-of-two-sorted-arrays/","LeetCode Hot 100"),
        ("Longest Palindromic Substring","Medium","String","Given a string s, return the longest palindromic substring.","Expand around center for each position. Check both odd and even length palindromes. Manacher algorithm can do O(n).","https://leetcode.com/problems/longest-palindromic-substring/","LeetCode Hot 100"),
        ("Zigzag Conversion","Medium","String","The string PAYPALISHIRING is written in a zigzag pattern on a given number of rows.","Simulate the zigzag pattern using an array of strings for each row. Track direction changes.","https://leetcode.com/problems/zigzag-conversion/","LeetCode Hot 100"),
        ("Reverse Integer","Medium","Math","Given a signed 32-bit integer x, return x with its digits reversed.","Pop digits using modulo, push to result. Check overflow before each push.","https://leetcode.com/problems/reverse-integer/","LeetCode Hot 100"),
        ("String to Integer (atoi)","Medium","String","Implement the myAtoi(string s) function.","Skip whitespace, check sign, read digits. Handle overflow by clamping to INT_MAX/INT_MIN. Community: state machine approach is elegant.","https://leetcode.com/problems/string-to-integer-atoi/","LeetCode Hot 100"),
        ("Palindrome Number","Easy","Math","Given an integer x, return true if x is a palindrome integer.","Reverse half the number and compare. Negative numbers are not palindromes.","https://leetcode.com/problems/palindrome-number/","LeetCode Hot 100"),
        ("Regular Expression Matching","Hard","String","Implement regular expression matching with support for '.' and '*'.","DP: dp[i][j] = does s[:i] match p[:j]. Handle '*' as zero or more of preceding element.","https://leetcode.com/problems/regular-expression-matching/","LeetCode Hot 100"),
        ("Container With Most Water","Medium","Array","Find two lines that together with the x-axis form a container that contains the most water.","Two pointers from both ends. Move the shorter line inward. Track max area.","https://leetcode.com/problems/container-with-most-water/","LeetCode Hot 100"),
        ("Integer to Roman","Medium","Math","Convert an integer to a Roman numeral.","Greedy approach using value-symbol pairs from largest to smallest.","https://leetcode.com/problems/integer-to-roman/","LeetCode Hot 100"),
        ("Roman to Integer","Easy","Math","Convert a Roman numeral to an integer.","If current value < next value, subtract current. Otherwise add.","https://leetcode.com/problems/roman-to-integer/","LeetCode Hot 100"),
        ("Longest Common Prefix","Easy","String","Write a function to find the longest common prefix string amongst an array of strings.","Horizontal scanning or vertical scanning. Community: sort and compare first/last.","https://leetcode.com/problems-longest-common-prefix/","LeetCode Hot 100"),
        ("3Sum","Medium","Array","Given an integer array nums, return all unique triplets that sum to zero.","Sort array, fix one element, use two pointers for remaining. Skip duplicates.","https://leetcode.com/problems/3sum/","LeetCode Hot 100"),
        ("3Sum Closest","Medium","Array","Given an array nums and a target, find three integers whose sum is closest to target.","Sort + two pointers. Track closest sum.","https://leetcode.com/problems/3sum-closest/","LeetCode Hot 100"),
        ("Letter Combinations of a Phone Number","Medium","String","Given a string containing digits 2-9, return all possible letter combinations.","Backtracking/DFS. Build combinations digit by digit using phone mapping.","https://leetcode.com/problems/letter-combinations-of-a-phone-number/","LeetCode Hot 100"),
        ("4Sum","Medium","Array","Given an array nums and target, return all unique quadruplets that sum to target.","Sort + two nested loops + two pointers. Skip duplicates at each level.","https://leetcode.com/problems/4sum/","LeetCode Hot 100"),
        ("Remove Nth Node From End of List","Medium","Linked List","Given the head of a linked list, remove the nth node from the end.","Two pointers with n gap. Use dummy head.","https://leetcode.com/problems/remove-nth-node-from-end-of-list/","LeetCode Hot 100"),
        ("Valid Parentheses","Easy","Stack","Given a string s containing just parentheses, determine if the input is valid.","Use stack. Push opening brackets, pop and match for closing.","https://leetcode.com/problems/valid-parentheses/","LeetCode Hot 100"),
        ("Merge Two Sorted Lists","Easy","Linked List","Merge two sorted linked lists into one sorted list.","Dummy head + pointer. Compare nodes, attach smaller one.","https://leetcode.com/problems/merge-two-sorted-lists/","LeetCode Hot 100"),
        ("Generate Parentheses","Medium","String","Generate all combinations of well-formed parentheses for n pairs.","Backtracking with open/close count. Add '(' if open < n, add ')' if close < open.","https://leetcode.com/problems/generate-parentheses/","LeetCode Hot 100"),
        ("Merge k Sorted Lists","Hard","Linked List","Merge k sorted linked lists into one sorted list.","Min-heap approach or divide and conquer merge. O(N log k).","https://leetcode.com/problems/merge-k-sorted-lists/","LeetCode Hot 100"),
        ("Swap Nodes in Pairs","Medium","Linked List","Given a linked list, swap every two adjacent nodes.","Iterative or recursive.","https://leetcode.com/problems/swap-nodes-in-pairs/","LeetCode Hot 100"),
        ("Reverse Nodes in k-Group","Hard","Linked List","Reverse the nodes of a linked list k at a time.","Count k nodes, reverse them, connect with previous group.","https://leetcode.com/problems/reverse-nodes-in-k-group/","LeetCode Hot 100"),
        ("Remove Duplicates from Sorted Array","Easy","Array","Remove duplicates in-place from sorted array, return new length.","Two pointers: slow for unique position, fast for scanning.","https://leetcode.com/problems/remove-duplicates-from-sorted-array/","LeetCode Hot 100"),
        ("Remove Element","Easy","Array","Remove all occurrences of val in nums in-place.","Two pointer: write pointer only advances when element != val.","https://leetcode.com/problems/remove-element/","LeetCode Hot 100"),
        ("Implement strStr()","Easy","String","Return the index of the first occurrence of needle in haystack.","KMP algorithm for O(n+m). Community: KMP next array is the core.","https://leetcode.com/problems/implement-strstr/","LeetCode Hot 100"),
        ("Divide Two Integers","Medium","Math","Divide two integers without using multiplication, division, or mod operator.","Bit manipulation. Shift divisor left until it's just less than dividend.","https://leetcode.com/problems/divide-two-integers/","LeetCode Hot 100"),
        ("Substring with Concatenation of All Words","Hard","String","Find all starting indices of substring(s) in s that is a concatenation of each word exactly once.","Sliding window with word-length steps. Use two hash maps.","https://leetcode.com/problems/substring-withcatenation-of-all-words/","LeetCode Hot 100"),
        ("Next Permutation","Medium","Array","Implement next permutation, which rearranges numbers into the next greater permutation.","Find first decreasing element from right, swap with smallest larger element, reverse suffix.","https://leetcode.com/problems/next-permutation/","LeetCode Hot 100"),
        ("Longest Valid Parentheses","Hard","String","Given a string containing just '(' and ')', find the length of the longest valid parentheses substring.","Stack approach: push indices. DP approach: dp[i] = length of longest valid ending at i.","https://leetcode.com/problems/longest-valid-parentheses/","LeetCode Hot 100"),
        ("Search in Rotated Sorted Array","Medium","Array","Search for target in a rotated sorted array.","Modified binary search. Determine which half is sorted, check if target is in sorted half.","https://leetcode.com/problems/search-in-rotated-sorted-array/","LeetCode Hot 100"),
        ("Find First and Last Position of Element in Sorted Array","Medium","Array","Given a sorted array, find the starting and ending position of a target value.","Two binary searches: one for leftmost, one for rightmost occurrence. O(log n).","https://leetcode.com/problems/find-first-and-last-position-of-element-in-sorted-array/","LeetCode Hot 100"),
        ("Search Insert Position","Easy","Array","Given a sorted array and a target value, return the index if found, else return insert position.","Standard binary search. Community: lower_bound template.","https://leetcode.com/problems-search-insert-position/","LeetCode Hot 100"),
        ("Valid Sudoku","Medium","Array","Determine if a 9x9 Sudoku board is valid.","Check rows, columns, and 3x3 boxes using sets.","https://leetcode.com/problems/valid-sudoku/","LeetCode Hot 100"),
        ("Sudoku Solver","Hard","Array","Write a program to solve a Sudoku puzzle.","Backtracking with pruning. Try each empty cell with valid numbers.","https://leetcode.com/problems/sudoku-solver/","LeetCode Hot 100"),
        ("Count and Say","Easy","String","The count-and-say sequence is a sequence of digit strings defined by the recursive formula.","Iterative simulation. Count consecutive digits.","https://leetcode.com/problems/count-and-say/","LeetCode Hot 100"),
        ("Combination Sum","Medium","Array","Find all unique combinations in candidates where the candidate numbers sum to target.","Backtracking with pruning. Sort first to enable early termination.","https://leetcode.com/problems/combination-sum/","LeetCode Hot 100"),
        ("Combination Sum II","Medium","Array","Find all unique combinations in candidates where each number is used only once.","Backtracking with sorting and skip duplicates.","https://leetcode.com/problems/combination-sum-ii/","LeetCode Hot 100"),
        ("First Missing Positive","Hard","Array","Given an unsorted integer array, find the smallest missing positive integer.","Cyclic sort: place each number at its correct index. O(n) time, O(1) space.","https://leetcode.com/problems/first-missing-positive/","LeetCode Hot 100"),
        ("Trapping Rain Water","Hard","Array","Given n non-negative integers representing an elevation map, compute how much water it can trap.","Two pointers from both sides. Track max left and right.","https://leetcode.com/problems/trapping-rain-water/","LeetCode Hot 100"),
        ("Multiply Strings","Medium","String","Given two non-negative integers num1 and num2 represented as strings, return the product.","Simulate multiplication digit by digit. Store results in array.","https://leetcode.com/problems/multiply-strings/","LeetCode Hot 100"),
        ("Wildcard Matching","Hard","String","Implement wildcard pattern matching with support for '?' and '*'.","DP or greedy with backtracking.","https://leetcode.com/problems/wildcard-matching/","LeetCode Hot 100"),
        ("Jump Game II","Medium","Array","Each element represents max jump length. Find minimum jumps to reach last index.","Greedy BFS. Track current reachable range and next reachable range.","https://leetcode.com/problems/jump-game-ii/","LeetCode Hot 100"),
        ("Permutations","Medium","Array","Given a collection of distinct integers, return all possible permutations.","Backtracking with swap or used array.","https://leetcode.com/problems/permutations/","LeetCode Hot 100"),
        ("Permutations II","Medium","Array","Given a collection of numbers that might contain duplicates, return all unique permutations.","Backtracking with sorting and skip duplicates.","https://leetcode.com/problems/permutations-ii/","LeetCode Hot 100"),
        ("Rotate Image","Medium","Array","You are given an n x n 2D matrix representing an image. Rotate the image by 90 degrees clockwise.","Transpose then reverse each row.","https://leetcode.com/problems/rotate-image/","LeetCode Hot 100"),
        ("Group Anagrams","Medium","String","Given an array of strings, group anagrams together.","Use sorted string as key in hash map.","https://leetcode.com/problems/group-anagrams/","LeetCode Hot 100"),
        ("Pow(x, n)","Medium","Math","Implement pow(x, n).","Fast exponentiation (binary exponentiation). O(log n).","https://leetcode.com/problems/powx-n/","LeetCode Hot 100"),
        ("N-Queens","Hard","Array","The n-queens puzzle is the problem of placing n queens on an n x n chessboard such that no two queens attack each other.","Backtracking row by row. Check column and diagonal conflicts using sets.","https://leetcode.com/problems/n-queens/","LeetCode Hot 100"),
        ("Maximum Subarray","Easy","Array","Given an integer array nums, find the subarray which has the largest sum.","Kadane's algorithm. Track current sum and max sum. Reset when current < 0.","https://leetcode.com/problems/maximum-subarray/","LeetCode Hot 100"),
        ("Spiral Matrix","Medium","Array","Given an m x n matrix, return all elements of the matrix in spiral order.","Use four boundaries: top, bottom, left, right. Shrink after each direction.","https://leetcode.com/problems/spiral-matrix/","LeetCode Hot 100"),
        ("Jump Game","Medium","Array","You are given an integer array nums. You are initially positioned at the first index.","Greedy: track the farthest reachable index. If current > farthest, return false.","https://leetcode.com/problems/jump-game/","LeetCode Hot 100"),
        ("Merge Intervals","Medium","Array","Given an array of intervals, merge all overlapping intervals.","Sort by start time. Merge if current start <= previous end.","https://leetcode.com/problems/merge-intervals/","LeetCode Hot 100"),
        ("Insert Interval","Medium","Array","You are given an array of non-overlapping intervals. Insert a new interval.","Three parts: before overlap, merge overlap, after overlap.","https://leetcode.com/problems/insert-interval/","LeetCode Hot 100"),
        ("Unique Paths","Medium","Array","A robot is located at the top-left corner of a m x n grid. Find unique paths.","DP: dp[i][j] = dp[i-1][j] + dp[i][j-1]. Space can be optimized to O(n).","https://leetcode.com/problems/unique-paths/","LeetCode Hot 100"),
        ("Climbing Stairs","Easy","Array","You are climbing a staircase. It takes n steps to reach the top. Each time you can climb 1 or 2 steps.","Fibonacci sequence. dp[i] = dp[i-1] + dp[i-2]. Space O(1).","https://leetcode.com/problems/climbing-stairs/","LeetCode Hot 100"),
        ("Edit Distance","Hard","String","Given two strings word1 and word2, return the minimum number of operations to convert word1 to word2.","DP: dp[i][j] = min operations to convert word1[:i] to word2[:j]. Insert, delete, replace.","https://leetcode.com/problems/edit-distance/","LeetCode Hot 100"),
        ("Longest Increasing Subsequence","Medium","Array","Given an integer array nums, return the length of the longest strictly increasing subsequence.","DP O(n^2) or patience sorting O(n log n). Binary search on tails array.","https://leetcode.com/problems/longest-increasing-subsequence/","LeetCode Hot 100"),
        ("Word Break","Medium","String","Given a string s and a dictionary of strings wordDict, return true if s can be segmented.","DP: dp[i] = true if s[:i] can be segmented. Check all possible last words.","https://leetcode.com/problems/word-break/","LeetCode Hot 100"),
        ("House Robber","Medium","Array","You are a professional robber planning to rob houses along a street.","DP: dp[i] = max(dp[i-1], dp[i-2] + nums[i]). Space O(1).","https://leetcode.com/problems/house-robber/","LeetCode Hot 100"),
        ("Coin Change","Medium","Array","You are given an integer array coins representing coins of different denominations.","DP: dp[i] = min coins to make amount i. For each coin, dp[i] = min(dp[i], dp[i-coin]+1).","https://leetcode.com/problems/coin-change/","LeetCode Hot 100"),
        ("Product of Array Except Self","Medium","Array","Given an integer array nums, return an array answer such that answer[i] is equal to the product of all elements except nums[i].","Prefix and suffix products. Left pass then right pass. O(n) time, O(1) extra space.","https://leetcode.com/problems/product-of-array-except-self/","LeetCode Hot 100"),
        ("Valid Anagram","Easy","String","Given two strings s and t, return true if t is an anagram of s.","Count character frequencies. Or sort both strings and compare.","https://leetcode.com/problems/valid-anagram/","LeetCode Hot 100"),
        ("Binary Tree Inorder Traversal","Easy","Tree","Given the root of a binary tree, return the inorder traversal of its nodes' values.","Recursive or iterative with stack. Morris traversal for O(1) space.","https://leetcode.com/problems/binary-tree-inorder-traversal/","LeetCode Hot 100"),
        ("Validate Binary Search Tree","Medium","Tree","Given the root of a binary tree, determine if it is a valid BST.","Recursive with min/max bounds. Or inorder traversal should be sorted.","https://leetcode.com/problems/validate-binary-search-tree/","LeetCode Hot 100"),
        ("Maximum Depth of Binary Tree","Easy","Tree","Given the root of a binary tree, return its maximum depth.","Recursive: 1 + max(depth(left), depth(right)). Or BFS level order.","https://leetcode.com/problems/maximum-depth-of-binary-tree/","LeetCode Hot 100"),
        ("Binary Tree Level Order Traversal","Medium","Tree","Given the root of a binary tree, return the level order traversal of its nodes' values.","BFS with queue. Process level by level.","https://leetcode.com/problems/binary-tree-level-order-traversal/","LeetCode Hot 100"),
        ("Serialize and Deserialize Binary Tree","Hard","Tree","Design an algorithm to serialize and deserialize a binary tree.","Preorder traversal with null markers. Use DFS for both operations.","https://leetcode.com/problems/serialize-and-deserialize-binary-tree/","LeetCode Hot 100"),
        ("Construct Binary Tree from Preorder and Inorder Traversal","Medium","Tree","Given two integer arrays preorder and inorder, construct and return the binary tree.","First element of preorder is root. Find root in inorder to split left/right subtrees.","https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/","LeetCode Hot 100"),
        ("Best Time to Buy and Sell Stock","Easy","Array","You are given an array prices. Find the maximum profit.","Track min price so far. Max profit = max(max profit, price - min price).","https://leetcode.com/problems/best-time-to-buy-and-sell-stock/","LeetCode Hot 100"),
        ("Number of Islands","Medium","Array","Given an m x n 2D binary grid which represents a map of '1's (land) and '0's (water).","DFS/BFS flood fill. Count connected components of 1s.","https://leetcode.com/problems/number-of-islands/","LeetCode Hot 100"),
        ("LRU Cache","Medium","Design","Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.","Hash map + doubly linked list. O(1) get and put.","https://leetcode.com/problems/lru-cache/","LeetCode Hot 100"),
        ("Min Stack","Medium","Stack","Design a stack that supports push, pop, top, and retrieving the minimum element in constant time.","Use auxiliary stack to track minimums. Or store min with each element.","https://leetcode.com/problems/min-stack/","LeetCode Hot 100"),
        ("Merge Sorted Array","Easy","Array","You are given two integer arrays nums1 and nums2, sorted in non-decreasing order.","Merge from the end. Three pointers: end of nums1, end of nums2, write position.","https://leetcode.com/problems/merge-sorted-array/","LeetCode Hot 100"),
        ("Decode Ways","Medium","String","A message containing letters from A-Z can be encoded into numbers.","DP: dp[i] = ways to decode s[:i]. Check single digit and two digit validity.","https://leetcode.com/problems/decode-ways/","LeetCode Hot 100"),
        ("Subsets","Medium","Array","Given an integer array nums of unique elements, return all possible subsets.","Backtracking. For each element, choose to include or exclude.","https://leetcode.com/problems/subsets/","LeetCode Hot 100"),
        ("Top K Frequent Elements","Medium","Array","Given an integer array nums and an integer k, return the k most frequent elements.","Bucket sort by frequency. Or min-heap of size k. O(n log k).","https://leetcode.com/problems/top-k-frequent-elements/","LeetCode Hot 100"),
        ("Course Schedule","Medium","Graph","There are a numCourses courses. Determine if it is possible to finish all courses.","Topological sort using BFS (Kahn's algorithm) or DFS cycle detection.","https://leetcode.com/problems/course-schedule/","LeetCode Hot 100"),
        ("Implement Trie (Prefix Tree)","Medium","Design","A trie (pronounced as 'try') or prefix tree is a tree data structure.","Each node has children map and isEnd flag. Insert and search are O(m) where m is word length.","https://leetcode.com/problems/implement-trie-prefix-tree/","LeetCode Hot 100"),
        ("Design Add and Search Words Data Structure","Medium","Design","Design a data structure that supports adding new words and finding if a string matches.","Trie with DFS for '.' wildcard matching.","https://leetcode.com/problems/design-add-and-search-words-data-structure/","LeetCode Hot 100"),
        ("Word Search II","Hard","String","Given an m x n board of characters and a list of strings words, return all words on the board.","Trie + DFS. Build trie from words, then DFS on board to find matches.","https://leetcode.com/problems/word-search-ii/","LeetCode Hot 100"),
        ("Maximum Product Subarray","Medium","Array","Given an integer array nums, find a subarray that has the largest product.","Track both max and min product ending at each position. Swap when negative.","https://leetcode.com/problems/maximum-product-subarray/","LeetCode Hot 100"),
        ("Find Minimum in Rotated Sorted Array","Medium","Array","Given the sorted array nums that has been rotated between 1 and n times.","Binary search. Compare mid with right to determine which half contains minimum.","https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/","LeetCode Hot 100"),
        ("Pacific Atlantic Water Flow","Medium","Array","There is an m x n rectangular island that borders both the Pacific and Atlantic oceans.","Reverse flow: start from oceans and flow uphill. Intersection of both reaches.","https://leetcode.com/problems/pacific-atlantic-water-flow/","LeetCode Hot 100"),
        ("Longest Consecutive Sequence","Medium","Array","Given an unsorted array of integers nums, return the length of the longest consecutive elements sequence.","Hash set. For each number, if num-1 not in set, count consecutive sequence starting from num.","https://leetcode.com/problems/longest-consecutive-sequence/","LeetCode Hot 100"),
        ("Graph Valid Tree","Medium","Graph","Given n nodes labeled from 0 to n-1 and a list of undirected edges, check if it's a valid tree.","A tree has exactly n-1 edges and is connected. Use Union-Find or DFS.","https://leetcode.com/problems/graph-valid-tree/","LeetCode Hot 100"),
        ("Number of Connected Components","Medium","Graph","Given n nodes and a list of edges, find the number of connected components.","Union-Find or DFS/BFS. Count distinct roots or DFS calls.","https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/","LeetCode Hot 100"),
        ("Alien Dictionary","Hard","Graph","Given a list of words sorted lexicographically in an alien language, return the order of letters.","Topological sort. Compare adjacent words to build character order graph.","https://leetcode.com/problems/alien-dictionary/","LeetCode Hot 100"),
        ("Meeting Rooms II","Medium","Array","Given an array of meeting time intervals, find the minimum number of conference rooms.","Min heap of end times. Or sweep line: sort starts and ends separately.","https://leetcode.com/problems/meeting-rooms-ii/","LeetCode Hot 100"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO recruitment_questions (title,difficulty,category,description,solution,reference_url,source) VALUES (?,?,?,?,?,?,?)",
        qs
    )


def seed_github(conn):
    if conn.execute("SELECT COUNT(*) FROM github_repos").fetchone()[0] >= 50:
        return
    repos = [
        ("tensorflow/tensorflow","https://github.com/tensorflow/tensorflow","An Open Source Machine Learning Framework","200000","Python","ML Framework"),
        ("pytorch/pytorch","https://github.com/pytorch/pytorch","Tensors and Dynamic neural networks","75000","Python","ML Framework"),
        ("huggingface/transformers","https://github.com/huggingface/transformers","State-of-the-art Machine Learning for JAX, PyTorch and TensorFlow","120000","Python","NLP"),
        ("microsoft/vscode","https://github.com/microsoft/vscode","Visual Studio Code","155000","TypeScript","Editor"),
        ("facebook/react","https://github.com/facebook/react","A declarative, efficient, and flexible JavaScript library","220000","JavaScript","Frontend"),
        ("vuejs/vue","https://github.com/vuejs/vue","Progressive JavaScript Framework","205000","JavaScript","Frontend"),
        ("golang/go","https://github.com/golang/go","The Go programming language","115000","Go","Language"),
        ("rust-lang/rust","https://github.com/rust-lang/rust","Empowering everyone to build reliable software","90000","Rust","Language"),
        ("kubernetes/kubernetes","https://github.com/kubernetes/kubernetes","Production-Grade Container Scheduling","105000","Go","DevOps"),
        ("docker/compose","https://github.com/docker/compose","Define and run multi-container applications","32000","Go","DevOps"),
        ("nodejs/node","https://github.com/nodejs/node","Node.js JavaScript runtime","100000","JavaScript","Runtime"),
        ("denoland/deno","https://github.com/deno/deno","A modern runtime for JavaScript and TypeScript","92000","Rust","Runtime"),
        ("vercel/next.js","https://github.com/vercel/next.js","The React Framework","118000","JavaScript","Frontend"),
        ("tailwindlabs/tailwindcss","https://github.com/tailwindlabs/tailwindcss","A utility-first CSS framework","78000","CSS","CSS Framework"),
        ("vitejs/vite","https://github.com/vitejs/vite","Next generation frontend tooling","62000","TypeScript","Build Tool"),
        ("neovim/neovim","https://github.com/neovim/neovim","Vim-fork focused on extensibility","75000","Vim Script","Editor"),
        ("ohmyzsh/ohmyzsh","https://github.com/ohmyzsh/ohmyzsh","A delightful community-driven framework for managing zsh configuration","165000","Shell","Tools"),
        ("awesome-selfhosted/awesome-selfhosted","https://github.com/awesome-selfhosted/awesome-selfhosted","A list of Free Software network services","160000","Markdown","Awesome List"),
        ("public-apis/public-apis","https://github.com/public-apis/public-apis","A collective list of free APIs","280000","Python","Awesome List"),
        ("sindresorhus/awesome","https://github.com/sindresorhus/awesome","Awesome lists about all kinds of interesting topics","290000","","Awesome List"),
        ("jwasham/coding-interview-university","https://github.com/jwasham/coding-interview-university","A complete computer science study plan","280000","","Interview Prep"),
        ("kamranahmedse/developer-roadmap","https://github.com/kamranahmedse/developer-roadmap","Interactive roadmaps, guides and educational content","265000","TypeScript","Learning"),
        ("EbookFoundation/free-programming-books","https://github.com/EbookFoundation/free-programming-books","Freely available programming books","300000","","Learning"),
        ("donnemartin/system-design-primer","https://github.com/donnemartin/system-design-primer","Learn how to design large-scale systems","245000","Python","System Design"),
        ("trekhleb/javascript-algorithms","https://github.com/trekhleb/javascript-algorithms","Algorithms and data structures implemented in JavaScript","180000","JavaScript","Algorithms"),
        ("TheAlgorithms/Python","https://github.com/TheAlgorithms/Python","All Algorithms implemented in Python","175000","Python","Algorithms"),
        ("codecrafters-io/build-your-own-x","https://github.com/codecrafters-io/build-your-own-x","Master programming by recreating your favorite technologies","240000","","Learning"),
        ("project-based-learning","https://github.com/practical-tutorials/project-based-learning","Curated list of project-based tutorials","160000","","Learning"),
        ("bradtraversy/design-resources-for-developers","https://github.com/bradtraversy/design-resources-for-developers","Curated list of design and UI resources","55000","","Design"),
        ("godotengine/godot","https://github.com/godotengine/godot","Godot Engine – Multi-platform 2D and 3D game engine","80000","C++","Game Engine"),
        ("flutter/flutter","https://github.com/flutter/flutter","Flutter makes it easy to build beautiful apps","160000","Dart","Mobile Framework"),
        ("microsoft/terminal","https://github.com/microsoft/terminal","The new Windows Terminal","92000","C++","Terminal"),
        ("starship/starship","https://github.com/starship/starship","The minimal, blazing-fast, and infinitely customizable prompt","40000","Rust","Terminal"),
        ("sharkdp/bat","https://github.com/sharkdp/bat","A cat(1) clone with wings","45000","Rust","CLI Tool"),
        ("ajeetdsouza/zoxide","https://github.com/ajeetdsouza/zoxide","A smarter cd command","15000","Rust","CLI Tool"),
        ("BurntSushi/ripgrep","https://github.com/BurntSushi/ripgrep","ripgrep recursively searches directories","42000","Rust","CLI Tool"),
        ("junegunn/fzf","https://github.com/junegunn/fzf","A command-line fuzzy finder","58000","Go","CLI Tool"),
        ("ohmybash/oh-my-bash","https://github.com/ohmybash/oh-my-bash","A delightful community-driven framework","5000","Shell","Shell"),
        ("NARKOZ/hacker-scripts","https://github.com/NARKOZ/hacker-scripts","Based on a true story","60000","","Fun"),
        ("danistefanovic/build-your-own-x","https://github.com/danistefanovic/build-your-own-x","Build your own (insert technology here)","220000","","Learning"),
        ("sveltejs/svelte","https://github.com/sveltejs/svelte","Cybernetically enhanced web apps","75000","JavaScript","Frontend"),
        ("solidjs/solid","https://github.com/solidjs/solid","A declarative, efficient, and flexible JavaScript library","30000","JavaScript","Frontend"),
        ("withastro/astro","https://github.com/withastro/astro","The all-in-one web framework","40000","TypeScript","Frontend"),
        ("remix-run/remix","https://github.com/remix-run/remix","Build Better Websites","260000","JavaScript","Frontend"),
        ("trpc/trpc","https://github.com/trpc/trpc","End-to-end typesafe APIs made easy","32000","TypeScript","Backend"),
        ("prisma/prisma","https://github.com/prisma/prisma","Next-generation ORM for Node.js and TypeScript","36000","TypeScript","Database"),
        ("supabase/supabase","https://github.com/supabase/supabase","The open source Firebase alternative","65000","TypeScript","Backend"),
        ("appwrite/appwrite","https://github.com/appwrite/appwrite","Secure backend server for Web, Mobile & Flutter developers","40000","PHP","Backend"),
        ("nuxt/nuxt","https://github.com/nuxt/nuxt","The Intuitive Vue Framework","50000","JavaScript","Frontend"),
        ("strapi/strapi","https://github.com/strapi/strapi","The leading open-source headless CMS","58000","JavaScript","CMS"),
        ("appium/appium","https://github.com/appium/appium","Automation for iOS and Android","18000","Python","Testing"),
        ("puppeteer/puppeteer","https://github.com/puppeteer/puppeteer","Headless Chrome Node API","85000","JavaScript","Testing"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO github_repos (name,url,description,stars,language,category) VALUES (?,?,?,?,?,?)",
        repos
    )


def seed_youtube(conn):
    if conn.execute("SELECT COUNT(*) FROM youtube_resources").fetchone()[0] >= 50:
        return
    resources = [
        ("CS50: Introduction to Computer Science","https://www.youtube.com/watch?v=8mAITcNt710","Harvard's introduction to computer science","Harvard CS50","CS Fundamentals"),
        ("Neural Networks - 3Blue1Brown","https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi","Visual introduction to neural networks","3Blue1Brown","Deep Learning"),
        ("Machine Learning - Andrew Ng","https://www.youtube.com/playlist?list=PLLssT5z_DsK-h9vYZkQkYNWcItqhlRJLN","Stanford Machine Learning course","Andrew Ng","Machine Learning"),
        ("Deep Learning Specialization","https://www.youtube.com/playlist?list=PLkDaE6sCZn6Ec-XTbcX1uRg2_u4xOEky0","DeepLearning.AI Deep Learning course","Andrew Ng","Deep Learning"),
        ("Algorithms - Abdul Bari","https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O","Algorithm explanations with examples","Abdul Bari","Algorithms"),
        ("System Design Primer","https://www.youtube.com/watch?v=MbjObHmDbZo","System design interview preparation","Gaurav Sen","System Design"),
        ("MIT 6.006 Introduction to Algorithms","https://www.youtube.com/playlist?list=PLUl4u3cNGP61Oq3tWYp6V_F-5jb5L2iHb","MIT Algorithms course","MIT OpenCourseWare","Algorithms"),
        ("Stanford CS229 Machine Learning","https://www.youtube.com/playlist?list=PLoROMvodv4rMiGQp3WXShtMGgzqpfVfbU","Stanford ML course","Stanford","Machine Learning"),
        ("Stanford CS231n CNN","https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8s-Y","Computer Vision and CNNs","Stanford","Computer Vision"),
        ("Stanford CS224n NLP","https://www.youtube.com/playlist?list=PLoROMvodv4rOhcuXMZkNm7j3fVwBBY42z","Natural Language Processing with Deep Learning","Stanford","NLP"),
        ("Fast.ai Practical Deep Learning","https://www.youtube.com/playlist?list=PLfYUBJi3iL231QGKz21IFZ7xJhh4xJvjz","Practical deep learning for coders","Fast.ai","Deep Learning"),
        ("Khan Academy - Algorithms","https://www.youtube.com/playlist?list=PLFD0EB975BA0CC1E0","Algorithm fundamentals","Khan Academy","Algorithms"),
        ("mycodeschool - Data Structures","https://www.youtube.com/playlist?list=PL2_aWCzGMAwI3W_JlcBbtYTwiQSsOTa6P","Data structures explained","mycodeschool","Data Structures"),
        ("Computerphile","https://www.youtube.com/playlist?list=PLzH6n4zXuckqmf_xUcvU5caZVoctP2eh","Computer science topics","Computerphile","CS Fundamentals"),
        ("Sentdex - Python ML","https://www.youtube.com/playlist?list=PLQVvvaa0QuDfKTOs3Keq_kaG2P55YRn5v","Python machine learning tutorials","Sentdex","Machine Learning"),
        ("Two Minute Papers","https://www.youtube.com/playlist?list=PLujxSBD-JXglGL3ERdDOhthD3D77BUFD_","AI research paper summaries","Two Minute Papers","AI Research"),
        ("Yannic Kilcher","https://www.youtube.com/playlist?list=PL1v7k-b6IHDV8Fg16bgy6SJ5gqdfswlCS","ML paper reading","Yannic Kilcher","AI Research"),
        ("AI Explained","https://www.youtube.com/playlist?list=PLQJ7yk9kMfFi5O1t7MwlGz8wCjiB0hWp","AI developments explained","AI Explained","AI Research"),
        ("Lex Fridman Podcast","https://www.youtube.com/playlist?list=PLrAXtmErZgOeiKm4sgNOknGvNjby9efdf","Conversations with AI researchers","Lex Fridman","Interviews"),
        ("Sebastian Lague","https://www.youtube.com/playlist?list=PLFt_AvXv10nN_0L5OFb5K1e3hE1pZ1q","Coding adventures and algorithms","Sebastian Lague","Programming"),
        ("The Coding Train","https://www.youtube.com/playlist?list=PLRqwX-V7Uu6ZiZxtDDRCi6uhfTH4FilpH","Creative coding with Processing","The Coding Train","Creative Coding"),
        ("Fireship","https://www.youtube.com/playlist?list=PL0vfts4VzfNiI1BsIK5u7LpPaIDKMJIDN","Quick tech explainers","Fireship","Web Development"),
        ("Traversy Media","https://www.youtube.com/playlist?list=PLillGF-RfqbZTASqIqdvm1R5mLrQq79NS","Web development tutorials","Traversy Media","Web Development"),
        ("Net Ninja","https://www.youtube.com/playlist?list=PL4cUxeGkcC9jsz4LDYc6kv3ymONOKxwBU","Modern JavaScript tutorials","Net Ninja","Web Development"),
        ("Tech With Tim","https://www.youtube.com/playlist?list=PLzMcBGfZo4-lp3jAExUCewBfMx3UZFkh5","Python programming tutorials","Tech With Tim","Python"),
        ("Sentdex Python","https://www.youtube.com/playlist?list=PLQVvvaa0QuDeAams7fkdc_i4flvFM884E","Python programming","Sentdex","Python"),
        ("Corey Schafer Python","https://www.youtube.com/playlist?list=PL-osiE80TeTt2d9bfVyTiXJA-UTHn6WwU","Python tutorials for all levels","Corey Schafer","Python"),
        ("freeCodeCamp","https://www.youtube.com/playlist?list=PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB","Free coding courses","freeCodeCamp","Learning"),
        ("CS Dojo","https://www.youtube.com/playlist?list=PLBZBJbE_rGRVnpitdvpdY9952IsKMDqFu","Programming and algorithms","CS Dojo","Programming"),
        ("Abdul Bari Algorithms","https://www.youtube.com/playlist?list=PLDN4rrl48XKpZkf03iYFl-O29szjTrs_O","Algorithm course","Abdul Bari","Algorithms"),
        ("WilliamFiset - Graph Theory","https://www.youtube.com/playlist?list=PLDV1Zeh2NRsDGO4--qE8yH72HFL1Km93P","Graph algorithms","WilliamFiset","Graph Theory"),
        ("Back To Back SWE","https://www.youtube.com/playlist?list=PLiQIPGOu0aX3x0FIgAM01V9qQKk9hHvJq","Software engineering interviews","Back To Back SWE","Interview Prep"),
        ("Clément Mihailescu","https://www.youtube.com/playlist?list=PLQpFMah8FkXnZ3hZ8C4FJ0X1J1q1q1q1","System design and algorithms","Clément Mihailescu","System Design"),
        ("Gaurav Sen","https://www.youtube.com/playlist?list=PLMCXHnjXnTnvo6alSjVkgxV-VH6EPyvoX","System design","Gaurav Sen","System Design"),
        ("ByteByteGo","https://www.youtube.com/playlist?list=PLCRMIe5FDPtegM1C0yO-DY13gNq1lB6l","System design explained","ByteByteGo","System Design"),
        ("Reducible","https://www.youtube.com/playlist?list=PL1BaGV1cIH4UhkL8a9NVGodWGrZh9khT","Algorithm visualizations","Reducible","Algorithms"),
        ("Spanning Tree","https://www.youtube.com/playlist?list=PL1BaGV1cIH4UhkL8a9NVGodWGrZh9khT","Math and CS concepts","Spanning Tree","CS Fundamentals"),
        ("Numberphile","https://www.youtube.com/playlist?list=PLt5AfwLFPxWJm9I1m3A0C4Y2n2v2v2v2","Math concepts","Numberphile","Math"),
        ("Computer Science","https://www.youtube.com/playlist?list=PLUl4u3cNGP63WbdFxL8giv4yhgdMGaZNA","MIT Distributed Systems","MIT","Distributed Systems"),
        ("NPTEL - Data Structures","https://www.youtube.com/playlist?list=PLBF3763AF2E1C572F","NPTEL Data Structures course","NPTEL","Data Structures"),
        ("Jenny's Lectures","https://www.youtube.com/playlist?list=PLdo5W4Nhv31bbKJzrsKfMpo_grxuLl8LU","CS lectures","Jenny's Lectures","CS Fundamentals"),
        ("Gate Smashers","https://www.youtube.com/playlist?list=PLxCzCOWd7aiF8nw8n7U1J2B2E1a1a1a1a","GATE CS preparation","Gate Smashers","Exam Prep"),
        ("mycodeschool OS","https://www.youtube.com/playlist?list=PLBlnK6fEyqRiVhbXDGLXDk_OQAeuVBYQ","Operating systems","mycodeschool","Operating Systems"),
        ("Neso Academy","https://www.youtube.com/playlist?list=PLBlnK6fEyqRj9lZCihVWTGjYYE1a1a1a1","Digital logic and COA","Neso Academy","Computer Architecture"),
        ("Abdul Bari OS","https://www.youtube.com/playlist?list=PLBlnK6fEyqRiVhbXDGLXDk_OQAeuVBYQ","Operating systems course","Abdul Bari","Operating Systems"),
        ("Javatpoint","https://www.youtube.com/playlist?list=PLBlnK6fEyqRj9lZCihVWTGjYYE1a1a1a1","Programming tutorials","Javatpoint","Programming"),
        ("Telusko","https://www.youtube.com/playlist?list=PLsyeobzWxl7poL9JTVyndKe62ieoN-MZ3","Java and Spring tutorials","Telusko","Java"),
        ("Amigoscode","https://www.youtube.com/playlist?list=PLwvrYc43l1Ixlx3gN1V1J1J1J1J1J1J1","Spring Boot and Java","Amigoscode","Java"),
        ("Derek Banas","https://www.youtube.com/playlist?list=PLGLfVvz_LVvQ5G-LdJ8RLqe-ndo7QITYc","Programming tutorials","Derek Banas","Programming"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO youtube_resources (title,url,description,channel,category) VALUES (?,?,?,?,?)",
        resources
    )


def seed_crypto(conn):
    if conn.execute("SELECT COUNT(*) FROM crypto_papers").fetchone()[0] >= 100:
        return
    papers = [
        ("Bitcoin: A Peer-to-Peer Electronic Cash System","Satoshi Nakamoto",2008,"The original Bitcoin whitepaper","提出去中心化电子现金系统，使用区块链和工作量证明解决双重支付问题。开创加密货币时代。","blockchain, cryptocurrency, consensus, proof-of-work","Whitepaper","https://bitcoin.org/bitcoin.pdf","Blockchain"),
        ("Ethereum: A Next-Generation Smart Contract Platform","Vitalik Buterin",2014,"Ethereum whitepaper","提出以太坊平台，支持智能合约和去中心化应用。开创了区块链2.0时代。","ethereum, smart contract, blockchain, dapp","Whitepaper","https://ethereum.org/en/whitepaper/","Blockchain"),
        ("A Next-Generation Smart Contract and Decentralized Application Platform","Buterin et al.",2014,"Ethereum technical yellowpaper","以太坊技术黄皮书，详细描述以太坊虚拟机(EVM)和状态转换函数。","EVM, state machine, gas, byzantium","Yellowpaper","https://ethereum.github.io/yellowpaper/paper.pdf","Blockchain"),
        ("On Lattices, Learning with Errors, Random Linear Codes, and Cryptography","Peikert",2009,"Ring-LWE and cryptographic applications","扩展LWE到环上版本Ring-LWE，提高效率同时保持安全性。Ring-LWE成为许多后量子方案基础。","Ring-LWE, lattice, efficiency, public key","STOC","","Post-Quantum"),
        ("Lattice-Based Cryptography","Oded Regev",2009,"Introduction to lattice-based cryptography","格密码学基于格上困难问题，具有抗量子攻击特性。介绍LWE问题及其在加密、签名中的应用。","lattice, LWE, post-quantum, encryption","ACM CCS","https://cims.nyu.edu/~regev/papers/lsurvey.pdf","Post-Quantum"),
        ("Fully Homomorphic Encryption Using Ideal Lattices","Craig Gentry",2009,"First construction of fully homomorphic encryption","首次构造全同态加密方案，基于理想格上困难问题。允许在密文上直接进行任意计算，被誉为密码学圣杯。","homomorphic encryption, ideal lattices, bootstrapping","STOC","https://dl.acm.org/doi/10.1145/1536414.1536440","Encryption"),
        ("Post-Quantum Cryptography","Bernstein, Buchmann, Dahmen",2009,"Comprehensive book on post-quantum cryptography","全面介绍后量子密码学，包括格密码、编码密码、多变量密码、哈希签名等抗量子方案。","post-quantum, lattice, code-based, multivariate, hash-based","Springer","","Post-Quantum"),
        ("Code-Based Cryptography","Overbeck, Sendrier",2009,"Survey of code-based cryptography","综述基于编码的密码学，包括McEliece和Niederreiter方案。McEliece是最早的后量子密码方案之一。","code-based, McEliece, Goppa code, post-quantum","Springer","","Post-Quantum"),
        ("Multivariate Public Key Cryptosystems","Ding, Gower, Schmidt",2006,"Multivariate cryptography","介绍多变量公钥密码系统，基于有限域上求解多变量方程组的困难性。","multivariate, MQ problem, oil-vinegar, public key","Springer","","Post-Quantum"),
        ("Hash-Based Signatures","Buchmann, Dahmen, Szydlo",2008,"Hash-based signature schemes","概述基于哈希的签名方案家族，包括XMSS和SPHINCS。哈希签名是最保守的后量子签名方案。","hash-based, XMSS, Merkle tree, one-time signature","Springer","","Signatures"),
        ("XMSS: Extended Hash-Based Signatures","Buchmann, Dahmen, Hülsing",2011,"XMSS signature scheme","XMSS是基于哈希的扩展签名方案，具有可证明安全性和实用性。支持前向安全性。","XMSS, hash-based, stateful, forward security","NIST","","Signatures"),
        ("Lightweight Cryptography for IoT","Katagi, Moriai",2011,"Lightweight cryptographic algorithms","讨论物联网环境下的轻量级密码学需求，包括PRESENT、SIMON、SPECK等算法。","lightweight, IoT, PRESENT, SIMON, SPECK","NIST","","Lightweight"),
        ("The Random Oracle Model: A Twenty-Year Retrospective","Bellare, Rogaway",2015,"Review of the random oracle model","回顾随机预言机模型20年发展，分析其在密码学证明中的优势和局限性。","random oracle, provable security, cryptographic proofs","ACM CCS","https://eprint.iacr.org/","Foundations"),
        ("SPHINCS: Practical Stateless Hash-Based Signatures","Bernstein et al.",2015,"SPHINCS stateless hash-based signatures","提出SPHINCS无状态哈希签名方案，是NIST后量子标准化候选方案。解决XMSS状态管理问题。","SPHINCS, hash-based, stateless, post-quantum","EUROCRYPT","","Post-Quantum"),
        ("The SKINNY Family of Block Ciphers","Beierle et al.",2016,"SKINNY lightweight block cipher","SKINNY是轻量级分组密码家族，支持多种块和密钥大小。设计简洁高效。","SKINNY, lightweight, block cipher, AES-like","CRYPTO","","Lightweight"),
        ("TFHE: Fast Fully Homomorphic Encryption Over the Torus","Chillotti et al.",2016,"TFHE fast bootstrapping","TFHE实现快速自举操作，使全同态加密在实际应用中更加可行。支持逐门自举。","TFHE, bootstrapping, FHE, torus, gate-by-gate","Journal of Cryptology","","Encryption"),
        ("CKKS: Homomorphic Encryption for Approximate Numbers","Cheon, Kim, Kim, Song",2017,"CKKS homomorphic encryption scheme","CKKS方案支持浮点数上的同态运算，适用于机器学习和统计分析。是FHE应用中最常用方案之一。","CKKS, homomorphic encryption, approximate arithmetic, FHE","ASIACRYPT","","Encryption"),
        ("SIKE: Supersingular Isogeny Key Encapsulation","Jao et al.",2017,"SIKE isogeny-based key encapsulation","SIKE基于超奇异椭圆曲线同构问题，是后量子密码学候选方案。曾被NIST选中但后来被破解。","SIKE, isogeny, elliptic curve, key encapsulation","PQCrypto","","Post-Quantum"),
        ("Zcash: Decentralized Anonymous Payments","Ben Sasson et al.",2014,"Zcash using zk-SNARKs","Zcash使用zk-SNARKs实现匿名交易，是零知识证明在区块链中的重要应用。","Zcash, zk-SNARK, blockchain, privacy, anonymous","IEEE S&P","","Blockchain"),
        ("zk-SNARKs: Zero-Knowledge Succinct Non-Interactive Arguments","Bitansky et al.",2012,"zk-SNARK construction","提出zk-SNARK构造，实现简洁零知识证明。证明大小恒定，验证时间极短。","zk-SNARK, zero-knowledge, succinct, QAP","STOC","","Cryptographic Protocols"),
        ("PLONK: Permutations over Lagrange-bases","Gabizon, Williamson, Ciobotaru",2019,"PLONK universal SNARK","PLONK是通用SNARK方案，支持通用和可更新可信设置。大大降低zk-SNARK使用门槛。","PLONK, SNARK, universal setup, polynomial commitment","ePrint","","Cryptographic Protocols"),
        ("STARKs: Scalable Transparent Arguments of Knowledge","Ben-Sasson et al.",2018,"STARK transparent proof system","STARK不需要可信设置，基于哈希函数，具有后量子安全性。证明大小对数增长。","STARK, transparent, hash-based, post-quantum, IOP","CRYPTO","","Cryptographic Protocols"),
        ("ASCON: Lightweight Authenticated Encryption","Dobraunig et al.",2019,"ASCON lightweight AEAD","ASCON被选为NIST轻量级密码标准，提供认证加密和哈希功能。设计简洁高效。","ASCON, lightweight, AEAD, hash, NIST","NIST LWC","","Lightweight"),
        ("CRYSTALS-Kyber: A CCA-Secure Module-Lattice-Based KEM","Bos et al.",2018,"Kyber key encapsulation mechanism","Kyber是基于模块格的密钥封装机制，被选为NIST后量子加密标准。具有高效实现和紧凑密钥。","Kyber, lattice, KEM, NIST, post-quantum","IEEE EuroS&P","","Post-Quantum"),
        ("CRYSTALS-Dilithium: Digital Signatures from Module Lattices","Ducas et al.",2018,"Dilithium digital signature scheme","Dilithium是基于模块格的数字签名方案，被选为NIST后量子签名标准。签名大小适中，验证高效。","Dilithium, lattice, signature, NIST, post-quantum","TCHES","","Post-Quantum"),
        ("FALCON: Fast-Fourier Lattice-Based Signatures over NTRU","Prest et al.",2019,"FALCON signature scheme","FALCON基于NTRU格和快速傅里叶变换，提供紧凑签名方案。是NIST后量子签名标准之一。","FALCON, NTRU, lattice, FFT, signature","NIST PQC","","Post-Quantum"),
        ("SEAL: Simple Encrypted Arithmetic Library","Microsoft Research",2015,"Microsoft SEAL library","微软SEAL库提供BFV和CKKS同态加密方案实现，推动FHE实际应用。","SEAL, BFV, CKKS, FHE, library","Microsoft","","Encryption"),
        ("NTRU Prime","Bernstein et al.",2016,"NTRU Prime post-quantum cryptosystem","NTRU Prime是NTRU改进版本，消除潜在结构性弱点。是后量子密码学候选方案。","NTRU Prime, lattice, post-quantum, cyclotomic","NIST PQC","","Post-Quantum"),
        ("Picnic: Post-Quantum Zero-Knowledge and Signatures","Chase et al.",2017,"Picnic post-quantum signature","Picnic基于零知识证明和对称密码原语，提供后量子安全的数字签名方案。","Picnic, ZK proof, symmetric, post-quantum","ACM CCS","","Post-Quantum"),
        ("BIKE: Bit Flipping Key Encapsulation","Aragon et al.",2017,"BIKE code-based KEM","BIKE是基于准循环中码的密钥封装机制，是NIST后量子标准化候选方案。","BIKE, code-based, QC-MDPC, KEM","NIST PQC","","Post-Quantum"),
        ("Classic McEliece","Bernstein et al.",2017,"Classic McEliece code-based encryption","Classic McEliece基于Goppa码，是最早的后量子加密方案之一。具有极小密文但很大公钥。","McEliece, Goppa code, code-based, NIST","NIST PQC","","Post-Quantum"),
        ("SIDH: Supersingular Isogeny Key Exchange","De Feo et al.",2011,"SIDH key exchange protocol","SIDH基于超奇异椭圆曲线同构问题，提供紧凑密钥交换方案。虽然后来被破解，但其思想仍有价值。","SIDH, isogeny, supersingular, key exchange","PQCrypto","","Post-Quantum"),
        ("Lattice Signatures Without Trapdoors","Lyubashevsky",2012,"Lattice-based signatures without trapdoors","提出不需要陷门的格签名方案，基于SIS问题。简化格签名构造。","lattice, signature, SIS, trapless","EUROCRYPT","","Post-Quantum"),
        ("BLISS: Bimodal Lattice Signature Schemes","Ducas et al.",2013,"BLISS signature scheme","BLISS是基于格的签名方案，使用双模态高斯分布。具有高效实现。","BLISS, lattice, Gaussian, signature","ACM CCS","","Post-Quantum"),
        ("Differential Privacy","Dwork et al.",2006,"Differential privacy definition","提出差分隐私的数学定义，为数据隐私保护提供严格理论基础。","differential privacy, data privacy, statistical","ICALP","","Privacy"),
        ("Garbled Circuits","Yao",1986,"Yao's garbled circuit protocol","提出混淆电路协议，是安全多方计算核心技术。允许两方在不泄露输入情况下计算任意函数。","garbled circuit, MPC, two-party","FOCS","","Cryptographic Protocols"),
        ("Threshold Cryptosystems","Desmedt, Frankel",1990,"Threshold cryptography","提出门限密码系统概念，密钥被分割成多个份额，需要至少t个份额才能执行密码操作。","threshold cryptography, distributed key generation","CRYPTO","","Key Exchange"),
        ("Oblivious Transfer and Polynomial Evaluation","Michael Rabin",1981,"Oblivious transfer protocol","提出不经意传输协议，是安全多方计算基础构件。","oblivious transfer, secure computation","FOCS","","Cryptographic Protocols"),
        ("The Complexity of Differential Privacy","Dwork, Roth",2014,"Differential privacy book","全面介绍差分隐私的理论和应用，是该领域标准参考书。","differential privacy, composition, mechanisms","Foundations and Trends in TCS","","Privacy"),
        ("Secure Computation with Fixed Computational Overhead","Ishai et al.",2010,"MPC with fixed overhead","提出具有固定计算开销的安全多方计算协议。","MPC, computational overhead, efficiency","CRYPTO","","Cryptographic Protocols"),
        ("Oblivious RAM: A Dissection","Boyle et al.",2016,"Oblivious RAM survey","综述不经意RAM研究进展，ORAM是保护数据访问模式的重要密码学原语。","ORAM, access pattern, privacy, survey","ACM Computing Surveys","","Cryptographic Protocols"),
        ("Bitcoin's Academic Pedigree","Narayanan, Clark",2017,"Bitcoin academic survey","全面回顾比特币的学术渊源，分析其与此前电子货币研究的关系。","bitcoin, cryptocurrency, survey, academic","ACM Queue","","Blockchain"),
        ("Algorand: Scaling Byzantine Agreements for Cryptocurrencies","Silvio Micali",2017,"Algorand consensus protocol","提出Algorand共识协议，使用密码学抽签实现高效拜占庭共识。","algorand, consensus, Byzantine agreement, crypto","PODC","","Blockchain"),
        ("Filecoin: A Decentralized Storage Network","Protocol Labs",2017,"Filecoin whitepaper","提出Filecoin去中心化存储网络，使用复制证明和时空证明。","filecoin, storage, proof of replication, blockchain","Whitepaper","","Blockchain"),
        ("Polkadot: Vision for a Heterogeneous Multi-Chain Framework","Gavin Wood",2016,"Polkadot whitepaper","提出Polkadot多链框架，实现跨链互操作性。","polkadot, multi-chain, interoperability, blockchain","Whitepaper","","Blockchain"),
        ("The Bitcoin Lightning Network","Poon, Dryja",2016,"Lightning Network whitepaper","提出闪电网络，实现比特币的链下快速支付通道。","lightning network, bitcoin, payment channel, layer 2","Whitepaper","","Blockchain"),
        ("Chainlink: A Decentralized Oracle Network","Ellis et al.",2017,"Chainlink whitepaper","提出Chainlink去中心化预言机网络，连接链上智能合约和链下数据。","chainlink, oracle, smart contract, blockchain","Whitepaper","","Blockchain"),
        ("Uniswap: A Decentralized Trading Protocol","Adams et al.",2018,"Uniswap protocol","提出Uniswap自动做市商协议，实现去中心化代币交易。","uniswap, AMM, DEX, defi","Whitepaper","","Blockchain"),
        ("Aave: Decentralized Lending Protocol","Kulechov et al.",2018,"Aave protocol","提出Aave去中心化借贷协议，支持闪电贷等创新功能。","aave, lending, defi, flash loan","Whitepaper","","Blockchain"),
        ("Compound: Algorithmic Money Market Protocol","Leshner et al.",2018,"Compound protocol","提出Compound算法货币市场协议，实现自动化借贷利率。","compound, money market, defi, interest rate","Whitepaper","","Blockchain"),
        ("MakerDAO: Stablecoin System","Maker Foundation",2017,"MakerDAO whitepaper","提出MakerDAO去中心化稳定币系统，使用超额抵押生成DAI。","makerdao, stablecoin, DAI, defi","Whitepaper","","Blockchain"),
        ("Curve: Efficient Stablecoin Exchange","Egorov",2019,"Curve protocol","提出Curve稳定币交换协议，优化稳定币之间的低滑点交易。","curve, stablecoin, AMM, defi","Whitepaper","","Blockchain"),
        ("Yearn Finance: Yield Aggregation","Andre Cronje",2020,"Yearn Finance","提出Yearn Finance收益聚合协议，自动优化DeFi收益策略。","yearn, yield aggregation, defi, vault","Whitepaper","","Blockchain"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO crypto_papers (title,authors,year,abstract,summary,keywords,venue,pdf_url,category) VALUES (?,?,?,?,?,?,?,?,?)",
        papers
    )


def seed_gnn(conn):
    if conn.execute("SELECT COUNT(*) FROM gnn_entities").fetchone()[0] >= 20:
        return
    entities = [
        ("User","Node",'{"features":["age","gender","interests","location","activity_level"]}',"用户节点，包含年龄、性别、兴趣、地理位置、活跃度等特征"),
        ("Item","Node",'{"features":["category","price","rating","popularity","brand"]}',"物品节点，包含类别、价格、评分、热度、品牌等特征"),
        ("Review","Node",'{"features":["rating","text","timestamp","sentiment"]}',"评论节点，包含评分、文本、时间戳、情感极性"),
        ("Category","Node",'{"features":["name","level","parent","item_count"]}',"类别节点，包含名称、层级、父类别、物品数量"),
        ("Brand","Node",'{"features":["name","country","reputation","market_share"]}',"品牌节点，包含名称、国家、声誉、市场份额"),
        ("Tag","Node",'{"features":["name","frequency","category"]}',"标签节点，包含名称、出现频率、所属类别"),
        ("Seller","Node",'{"features":["name","rating","location","verified"]}',"卖家节点，包含名称、评分、位置、认证状态"),
        ("Coupon","Node",'{"features":["type","value","min_purchase","expiry"]}',"优惠券节点，包含类型、面值、最低消费、有效期"),
        ("Purchase","Edge",'{"weight":"count"}',"购买关系，权重为购买次数"),
        ("View","Edge",'{"weight":"duration"}',"浏览关系，权重为浏览时长"),
        ("BelongTo","Edge",'{"weight":1.0}',"属于关系，物品属于某个类别"),
        ("ProducedBy","Edge",'{"weight":1.0}',"生产关系，物品由某品牌生产"),
        ("SimilarTo","Edge",'{"weight":"similarity"}',"相似关系，基于特征相似度"),
        ("BoughtTogether","Edge",'{"weight":"co_occurrence"}',"共同购买关系，基于共现频率"),
        ("TaggedWith","Edge",'{"weight":"relevance"}',"标签关系，基于相关性分数"),
        ("SoldBy","Edge",'{"weight":1.0}',"销售关系，物品由某卖家销售"),
        ("UsedCoupon","Edge",'{"weight":1.0}',"使用优惠券关系"),
        ("Follows","Edge",'{"weight":1.0}',"关注关系，用户关注卖家或品牌"),
        ("Rated","Edge",'{"weight":"rating"}',"评分关系，用户对物品的评分"),
        ("Influences","Edge",'{"weight":"strength"}',"影响关系，用户之间的社交影响"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO gnn_entities (name,entity_type,properties,description) VALUES (?,?,?,?)",
        entities
    )
    # Seed relations
    if conn.execute("SELECT COUNT(*) FROM gnn_relations").fetchone()[0] == 0:
        # Get entity IDs
        def get_id(name):
            row = conn.execute("SELECT id FROM gnn_entities WHERE name=?", (name,)).fetchone()
            return row[0] if row else None
        relations = [
            (get_id("User"), get_id("Purchase"), "purchases", 1.0),
            (get_id("User"), get_id("View"), "views", 1.0),
            (get_id("User"), get_id("Rated"), "rates", 1.0),
            (get_id("User"), get_id("Follows"), "follows", 1.0),
            (get_id("User"), get_id("Influences"), "influences", 0.8),
            (get_id("Item"), get_id("BelongTo"), "belongs_to", 1.0),
            (get_id("Item"), get_id("ProducedBy"), "produced_by", 1.0),
            (get_id("Item"), get_id("SimilarTo"), "similar_to", 0.9),
            (get_id("Item"), get_id("BoughtTogether"), "bought_with", 0.7),
            (get_id("Item"), get_id("TaggedWith"), "tagged_with", 1.0),
            (get_id("Item"), get_id("SoldBy"), "sold_by", 1.0),
            (get_id("Review"), get_id("Rated"), "is_rating_of", 1.0),
            (get_id("Coupon"), get_id("UsedCoupon"), "used_by", 1.0),
            (get_id("Brand"), get_id("ProducedBy"), "produces", 1.0),
            (get_id("Seller"), get_id("SoldBy"), "sells", 1.0),
        ]
        relations = [(s, t, r, w) for s, t, r, w in relations if s and t]
        conn.executemany(
            "INSERT INTO gnn_relations (source_id, target_id, relation_type, weight) VALUES (?,?,?,?)",
            relations
        )


def seed_investment(conn):
    if conn.execute("SELECT COUNT(*) FROM investment_records").fetchone()[0] >= 8:
        return
    records = [
        ("Apple Inc.","Stock",10000,15.2,"Medium","长期持有，科技龙头"),
        ("S&P 500 ETF","ETF",15000,8.5,"Low","分散投资，稳健增长"),
        ("Bitcoin","Crypto",5000,45.0,"High","高风险高回报"),
        ("Real Estate Fund","Fund",20000,6.0,"Medium","房地产投资信托"),
        ("Government Bonds","Bond",30000,3.5,"Low","稳定收益，低风险"),
        ("Tesla Inc.","Stock",8000,22.0,"High","新能源汽车龙头"),
        ("Gold ETF","Commodity",5000,4.0,"Low","避险资产"),
        ("Emerging Markets ETF","ETF",7000,10.0,"Medium","新兴市场增长潜力"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO investment_records (name,asset_type,amount,return_rate,risk_level,notes) VALUES (?,?,?,?,?,?)",
        records
    )


def seed_makeup(conn):
    if conn.execute("SELECT COUNT(*) FROM makeup_tips").fetchone()[0] >= 30:
        return
    tips = [
        ("日常底妆","Base","1. 洁面后使用保湿乳液\\n2. 涂抹妆前乳\\n3. 用海绵均匀推开粉底液\\n4. 遮瑕膏点涂瑕疵\\n5. 散粉定妆","Beginner"),
        ("眼妆基础","Eyes","1. 浅色眼影打底\\n2. 中间色涂眼窝\\n3. 深色加深眼尾\\n4. 画眼线\\n5. 刷睫毛膏","Beginner"),
        ("眉毛画法","Brows","1. 修眉确定眉形\\n2. 眉头轻画\\n3. 眉峰加重\\n4. 眉尾自然收细\\n5. 眉刷晕染自然","Beginner"),
        ("腮红技巧","Cheeks","1. 微笑找到苹果肌\\n2. 从太阳穴向苹果肌扫\\n3. 少量多次叠加\\n4. 与肤色协调的色号","Beginner"),
        ("唇妆技巧","Lips","1. 唇部去角质\\n2. 润唇膏打底\\n3. 唇线笔勾勒\\n4. 口红填充\\n5. 纸巾轻压定妆","Beginner"),
        ("修容高光","Contour","1. 修容粉涂颧骨下方\\n2. 鼻影从眉头到鼻尖\\n3. 高光涂T区\\n4. 高光涂颧骨上方\\n5. 自然晕染过渡","Intermediate"),
        ("烟熏妆","Eyes","1. 深色眼影打底\\n2. 黑色眼影涂眼窝\\n3. 下眼影晕染\\n4. 浓黑眼线\\n5. 浓密睫毛膏","Advanced"),
        ("日系妆容","Style","1. 清透底妆\\n2. 自然眉形\\n3. 粉色系眼影\\n4. 自然腮红\\n5. 水润唇妆","Intermediate"),
        ("韩系妆容","Style","1. 水光肌底妆\\n2. 平直眉\\n3. 大地色眼影\\n4. 卧蚕提亮\\n5. 渐变唇妆","Intermediate"),
        ("欧美妆容","Style","1. 无瑕底妆\\n2. 立体修容\\n3. 截断式眼妆\\n4. 浓密睫毛\\n5. 丰满唇妆","Advanced"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO makeup_tips (title,category,content,difficulty) VALUES (?,?,?,?)",
        tips
    )


def seed_fashion(conn):
    if conn.execute("SELECT COUNT(*) FROM fashion_items").fetchone()[0] >= 33:
        return
    items = [
        ("白衬衫","Top","All","White","Classic","百搭单品，可正式可休闲。搭配牛仔裤是休闲风，搭配西裤是职场风。选真丝或高支棉更显质感。"),
        ("牛仔裤","Bottom","All","Blue","Casual","经典牛仔裤，修身版型。直筒裤适合所有身材，阔腿裤显瘦显高。深色更正式，浅色更休闲。"),
        ("小黑裙","Dress","Summer","Black","Elegant","优雅小黑裙，适合各种场合。及膝长度最百搭，V领显瘦，A字版型遮肉。搭配高跟鞋是晚宴风，搭配平底鞋是日常风。"),
        ("风衣","Outerwear","Spring/Fall","Beige","Classic","经典卡其风衣，春秋必备。双排扣设计更经典，腰带可以打造X型身材。长度到膝盖最显高。"),
        ("针织衫","Top","Winter","Gray","Casual","温暖舒适的针织毛衣。羊绒材质最柔软，粗针织有慵懒感。塞进裤子显腿长，放下来更休闲。"),
        ("西装套装","Set","All","Navy","Formal","正式商务西装，展现专业形象。深蓝色最显瘦，收腰设计更修身。内搭白衬衫是经典，搭高领毛衣更时尚。"),
        ("运动鞋","Shoes","All","White","Sporty","百搭运动鞋，舒适时尚。小白鞋配什么都好看，厚底款显高。定期清洗保持白净。"),
        ("高跟鞋","Shoes","All","Black","Elegant","经典黑色高跟鞋。7cm是最舒适的高度，尖头显瘦，粗跟更稳。裸色款显腿长。"),
        ("围巾","Accessory","Winter","Red","Classic","保暖又时尚的围巾。羊绒围巾最柔软，大围巾可以当披肩。红色提亮整体造型。"),
        ("太阳镜","Accessory","Summer","Black","Trendy","时尚太阳镜，保护眼睛。圆脸选方脸，方脸选圆脸。偏光镜片更护眼。"),
        ("条纹T恤","Top","Summer","Navy/White","Casual","法式经典单品，条纹越细越显瘦。搭配牛仔裤是经典法式风，搭配白色阔腿裤更清爽。"),
        ("阔腿裤","Bottom","Fall/Winter","Black","Minimalist","显瘦显高的神器。高腰设计拉长腿部线条，搭配短上衣效果最好。选垂感面料更高级。"),
        ("A字裙","Dress","Spring/Summer","Floral","Feminine","遮肉显瘦的万能单品。长度到膝盖上方5cm最显高。碎花款适合度假，纯色款适合通勤。"),
        ("皮夹克","Outerwear","Fall","Black","Streetwear","酷帅必备单品。搭配连衣裙是娘man平衡，搭配T恤牛仔裤是经典摇滚风。选羊皮更柔软。"),
        ("大衣","Outerwear","Winter","Camel","Classic","冬季必备高级感单品。驼色最经典，H型版型最显瘦。长度到小腿中部最显高。"),
        ("乐福鞋","Shoes","Spring/Fall","Brown","Preppy","学院风经典单品。搭配九分裤露出脚踝最显瘦。金属扣款更正式，流苏款更休闲。"),
        ("帆布包","Bag","Summer","White","Casual","夏日清爽单品。白色最百搭，搭配碎花裙是法式风。选厚实的帆布更耐用。"),
        ("链条包","Bag","All","Black","Elegant","精致小包，适合约会和晚宴。金色链条更华丽，银色链条更低调。选小号更精致。"),
        ("珍珠项链","Jewelry","All","White","Classic","优雅必备。单层短链最百搭，多层叠戴更时尚。搭配V领上衣效果最好。"),
        ("金色耳环","Jewelry","All","Gold","Trendy","提亮整体造型。小耳钉日常百搭，大耳环适合派对。圆脸选长款，长脸选圆款。"),
        ("棒球帽","Accessory","Summer","Black","Streetwear","休闲运动风必备。搭配马尾辫最清爽，反戴更有个性。选棉质更透气。"),
        ("贝雷帽","Accessory","Fall/Winter","Red","Bohemian","法式浪漫单品。斜戴最时髦，搭配大衣是经典法式风。红色最提亮，黑色最百搭。"),
        ("丝巾","Accessory","Spring","Multicolor","Classic","万能配饰。系在脖子上是优雅，系在包上是时尚，系在头发上是浪漫。选真丝材质最高级。"),
        ("马丁靴","Shoes","Fall/Winter","Black","Streetwear","酷帅百搭。8孔最经典，搭配牛仔裤是摇滚风，搭配裙子是混搭风。选硬皮更有型。"),
        ("百褶裙","Dress","Spring","Plaid","Preppy","学院风代表。格纹款最经典，搭配白衬衫是校服风。长度到膝盖最优雅。"),
        ("吊带裙","Dress","Summer","White","Minimalist","夏日清凉单品。内搭T恤是休闲风，单穿是度假风。选棉麻材质更透气。"),
        ("卫衣","Top","Fall","Gray","Streetwear","舒适休闲必备。oversize款最时髦，搭配紧身裤是上大下小。连帽款更休闲，圆领款更百搭。"),
        ("衬衫裙","Dress","Summer","Blue","Classic","一件式穿搭，省时省力。系腰带显瘦，搭配平底鞋是休闲风，搭配高跟鞋是通勤风。"),
        ("皮裤","Bottom","Winter","Black","Trendy","酷帅单品。搭配毛衣是休闲风，搭配衬衫是通勤风。选弹力面料更舒适。"),
        ("羽绒服","Outerwear","Winter","White","Casual","保暖必备。短款显高，长款更保暖。白色最清爽，黑色最显瘦。选90%含绒量更保暖。"),
        ("高领毛衣","Top","Winter","Black","Minimalist","冬季内搭神器。搭配大衣是经典，搭配西装是时尚。选羊绒材质最柔软保暖。"),
        ("水桶包","Bag","All","Tan","Casual","实用又时尚。容量大适合日常，搭配休闲装最合适。棕色最百搭。"),
        ("墨镜夹片","Accessory","Summer","Black","Trendy","近视党的福音。夹在近视眼镜上就能防晒。选偏光镜片效果更好。"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO fashion_items (name,category,season,color,style,description) VALUES (?,?,?,?,?,?)",
        items
    )


def seed_cooking(conn):
    if conn.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] >= 30:
        return
    recipes = [
        ("番茄炒蛋","Chinese","Easy",15,"番茄2个, 鸡蛋3个, 葱花, 盐, 糖, 油","1. 鸡蛋打散炒熟盛出\\n2. 番茄切块翻炒出汁\\n3. 加入炒蛋混合\\n4. 调味撒葱花出锅","番茄要炒出汁才好吃"),
        ("红烧肉","Chinese","Medium",60,"五花肉500g, 冰糖, 生抽, 老抽, 料酒, 姜片, 八角","1. 肉切块焯水\\n2. 冰糖炒糖色\\n3. 下肉块翻炒上色\\n4. 加调料炖煮45分钟\\n5. 大火收汁","糖色不要炒糊"),
        ("宫保鸡丁","Chinese","Medium",30,"鸡胸肉300g, 花生米, 干辣椒, 花椒, 葱姜蒜","1. 鸡肉切丁腌制\\n2. 炸花生米\\n3. 炒鸡丁至变色\\n4. 加辣椒花椒炒香\\n5. 调味勾芡","鸡丁要大火快炒"),
        ("麻婆豆腐","Chinese","Easy",20,"豆腐1块, 肉末, 豆瓣酱, 花椒粉, 葱花","1. 豆腐切块焯水\\n2. 炒肉末加豆瓣酱\\n3. 加水煮豆腐\\n4. 勾芡撒花椒粉","豆腐不要翻动太多"),
        ("意大利面","Western","Easy",20,"意大利面200g, 番茄酱, 洋葱, 蒜, 橄榄油","1. 煮面至al dente\\n2. 炒香洋葱蒜末\\n3. 加番茄酱熬制\\n4. 面条拌入酱汁","煮面要加盐"),
        ("牛排","Western","Medium",20,"牛排200g, 黄油, 蒜, 迷迭香, 黑胡椒, 盐","1. 牛排回温调味\\n2. 热锅煎至所需熟度\\n3. 加黄油蒜迷迭香\\n4. 静置5分钟再切","不要频繁翻面"),
        ("寿司卷","Japanese","Hard",45,"寿司米, 海苔, 三文鱼, 黄瓜, 蟹肉棒","1. 煮寿司米调味\\n2. 海苔铺米饭\\n3. 放馅料卷紧\\n4. 刀沾水切段","卷的时候要紧实"),
        ("咖喱饭","Japanese","Easy",40,"咖喱块, 土豆, 胡萝卜, 洋葱, 鸡肉","1. 蔬菜切块\\n2. 炒肉和蔬菜\\n3. 加水煮软\\n4. 加咖喱块融化","咖喱块要关火再加"),
        ("韩式拌饭","Korean","Medium",30,"米饭, 菠菜, 豆芽, 胡萝卜, 牛肉, 鸡蛋, 韩式辣酱","1. 蔬菜分别炒熟\\n2. 牛肉腌制炒熟\\n3. 煎太阳蛋\\n4. 摆盘拌辣酱","蔬菜要分开炒"),
        ("冬阴功汤","Thai","Medium",30,"虾, 蘑菇, 柠檬草, 青柠, 椰浆, 辣椒","1. 煮香茅和辣椒\\n2. 加蘑菇和虾\\n3. 加椰浆调味\\n4. 挤青柠汁","青柠汁最后加"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO recipes (name,cuisine,difficulty,cook_time,ingredients,steps,tips) VALUES (?,?,?,?,?,?,?)",
        recipes
    )


def seed_study_abroad(conn):
    if conn.execute("SELECT COUNT(*) FROM study_abroad").fetchone()[0] >= 30:
        return
    programs = [
        ("USA","MIT","MS in Computer Science","GPA 3.5+, GRE 320+, TOEFL 100+","Dec 15","需要推荐信3封。学费约$55K/年，生活费$20K/年。STEM专业有3年OPT。"),
        ("USA","Stanford","MS in AI","GPA 3.7+, GRE 325+, TOEFL 105+","Dec 1","看重科研经历。学费约$56K/年。硅谷实习机会多。"),
        ("USA","Carnegie Mellon","MS in Machine Learning","GPA 3.5+, GRE 320+, TOEFL 100+","Dec 15","ML专业全美第一。学费约$50K/年。"),
        ("USA","UC Berkeley","MEng in EECS","GPA 3.5+, GRE 320+, TOEFL 100+","Jan 5","1年制工程硕士。学费约$55K/年。"),
        ("UK","Oxford","MSc in Computer Science","First Class, IELTS 7.5","Jan 15","需要研究计划。学费约£30K/年。1年制。"),
        ("UK","Cambridge","MPhil in ML","First Class, IELTS 7.5","Dec 1","需要面试。学费约£35K/年。研究型硕士。"),
        ("UK","Imperial College","MSc in Computing","2:1, IELTS 7.0","Rolling","伦敦地理位置好。学费约£35K/年。"),
        ("UK","UCL","MSc in Data Science","2:1, IELTS 7.0","Mar 31","学费约£32K/年。课程实用。"),
        ("Canada","University of Toronto","MSc in CS","GPA 3.3+, IELTS 7.0","Feb 1","可申请奖学金。学费约CAD 28K/年。2年制。"),
        ("Canada","UBC","MSc in CS","GPA 3.0+, IELTS 6.5","Jan 15","温哥华气候好。学费约CAD 9K/年(研究型)。"),
        ("Canada","University of Waterloo","MMath in CS","GPA 3.3+, IELTS 7.0","Feb 1","Co-op项目著名。学费约CAD 20K/年。"),
        ("Australia","University of Melbourne","Master of IT","GPA 3.0+, IELTS 6.5","Oct 31","2年制有工签。学费约AUD 45K/年。"),
        ("Australia","ANU","Master of Computing","GPA 3.0+, IELTS 6.5","Dec 15","堪培拉安静适合学习。学费约AUD 48K/年。"),
        ("Australia","UNSW","Master of IT","GPA 3.0+, IELTS 6.5","Mar 31","悉尼就业机会多。学费约AUD 47K/年。"),
        ("Germany","TU Munich","MSc in Informatics","GPA 2.5+, IELTS 6.5","Mar 15","免学费，仅注册费€150/学期。世界顶尖工科。"),
        ("Germany","RWTH Aachen","MSc in CS","GPA 2.5+, IELTS 6.5","Mar 15","免学费。工科强校。"),
        ("Singapore","NUS","MSc in CS","GPA 3.5+, IELTS 6.5","Jan 31","亚洲顶尖。学费约SGD 45K/年。可申请奖学金。"),
        ("Singapore","NTU","MSc in AI","GPA 3.3+, IELTS 6.5","Feb 28","学费约SGD 50K/年。AI专业强。"),
        ("Japan","University of Tokyo","MSc in CS","GPA 3.0+, TOEFL 90+","Dec 1","可申请MEXT奖学金(免学费+生活费)。学费约¥540K/年。"),
        ("Japan","Kyoto University","MSc in CS","GPA 3.0+, TOEFL 90+","Dec 1","学费约¥540K/年。研究氛围好。"),
        ("Netherlands","TU Delft","MSc in CS","GPA 3.0+, IELTS 6.5","Apr 1","欧洲硅谷。学费约€18K/年。2年制。"),
        ("Netherlands","University of Amsterdam","MSc in AI","GPA 3.0+, IELTS 6.5","Apr 1","学费约€16K/年。AI研究强。"),
        ("Switzerland","ETH Zurich","MSc in CS","GPA 3.5+, IELTS 7.0","Dec 15","世界顶尖。学费仅CHF 1.5K/学期。生活成本高。"),
        ("Switzerland","EPFL","MSc in CS","GPA 3.5+, IELTS 7.0","Dec 15","学费约CHF 1.3K/学期。"),
        ("France","Sorbonne University","MSc in CS","GPA 3.0+, IELTS 6.5","Mar 31","学费约€3K/年。法语环境。"),
        ("Sweden","KTH Royal Institute","MSc in CS","GPA 3.0+, IELTS 6.5","Jan 15","学费约SEK 160K/年。免学费对EU学生。"),
        ("Sweden","Chalmers University","MSc in CS","GPA 3.0+, IELTS 6.5","Jan 15","学费约SEK 160K/年。"),
        ("Hong Kong","HKU","MSc in CS","GPA 3.3+, IELTS 6.5","Feb 1","学费约HKD 170K/年。1年制。"),
        ("Hong Kong","HKUST","MSc in IT","GPA 3.3+, IELTS 6.5","Feb 1","学费约HKD 150K/年。"),
        ("Hong Kong","CUHK","MSc in CS","GPA 3.0+, IELTS 6.5","Feb 28","学费约HKD 130K/年。"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO study_abroad (country,university,program,requirements,deadline,notes) VALUES (?,?,?,?,?,?)",
        programs
    )


def seed_civil_exam(conn):
    if conn.execute("SELECT COUNT(*) FROM civil_exam").fetchone()[0] >= 42:
        return
    topics = [
        ('行政职业能力测验', '言语理解-阅读理解', '主旨概括、意图判断、细节理解、词句理解、标题填入、态度观点', '选择题'),
        ('行政职业能力测验', '言语理解-逻辑填空', '实词辨析、成语辨析、混搭填空、虚词填空', '选择题'),
        ('行政职业能力测验', '言语理解-语句表达', '语句排序、语句填空、接语选择题', '选择题'),
        ('行政职业能力测验', '数量关系-数字推理', '等差数列、等比数列、和数列、积数列、幂数列、分数数列', '选择题'),
        ('行政职业能力测验', '数量关系-数学运算', '行程问题、工程问题、利润问题、排列组合、概率问题、几何问题', '选择题'),
        ('行政职业能力测验', '判断推理-图形推理', '位置类、样式类、数量类、属性类、功能类、立体图形', '选择题'),
        ('行政职业能力测验', '判断推理-定义判断', '单定义、多定义、肯定型、否定型', '选择题'),
        ('行政职业能力测验', '判断推理-类比推理', '语法关系、语义关系、逻辑关系（全同、包含、交叉、并列、对应）', '选择题'),
        ('行政职业能力测验', '判断推理-逻辑判断', '翻译推理、组合排列、逻辑论证、原因解释、归纳推理', '选择题'),
        ('行政职业能力测验', '资料分析-增长率', '同比增长率、环比增长率、年均增长率、混合增长率', '选择题'),
        ('行政职业能力测验', '资料分析-增长量', '增长量计算、增长量比较、年均增长量', '选择题'),
        ('行政职业能力测验', '资料分析-比重', '现期比重、基期比重、两期比重比较', '选择题'),
        ('行政职业能力测验', '资料分析-平均数', '现期平均数、基期平均数、两期平均数比较', '选择题'),
        ('行政职业能力测验', '常识判断-政治', '马克思主义哲学、毛泽东思想、中国特色社会主义理论体系、时政', '选择题'),
        ('行政职业能力测验', '常识判断-法律', '宪法、行政法、民法、刑法、诉讼法', '选择题'),
        ('行政职业能力测验', '常识判断-经济', '微观经济（供给需求、市场结构）、宏观经济（财政货币政策）、国际经济', '选择题'),
        ('行政职业能力测验', '常识判断-历史', '中国古代史、中国近现代史、世界史', '选择题'),
        ('行政职业能力测验', '常识判断-地理', '自然地理、人文地理、中国地理、世界地理', '选择题'),
        ('行政职业能力测验', '常识判断-科技', '物理化学生物常识、前沿科技、生活科技', '选择题'),
        ('申论', '归纳概括题', '概括主要内容、问题、原因、影响、特点', '简答题'),
        ('申论', '提出对策题', '针对问题提出解决方案、建议、措施', '简答题'),
        ('申论', '综合分析题', '对观点、现象、词语进行分析评价', '答题模板'),
        ('申论', '贯彻执行题', '撰写公文、应用文（讲话稿、倡议书、通知、报告等）', '应用文写作'),
        ('申论', '大作文', '议论文写作', '论述题'),
        ('面试', '结构化面试', '综合分析、计划组织、应急应变、人际关系、求职动机', '面试题'),
        ('面试', '无领导小组讨论', '开放式问题、两难问题、多项选择、资源争夺', '面试题'),
        ('公共基础知识', '马克思主义哲学-唯物论', '物质与意识、运动与静止、规律的客观性', '选择题'),
        ('公共基础知识', '马克思主义哲学-辩证法', '联系观、发展观、矛盾观、辩证否定观', '选择题'),
        ('公共基础知识', '马克思主义哲学-认识论', '实践与认识、真理与谬误、认识的反复性和无限性', '选择题'),
        ('公共基础知识', '马克思主义哲学-唯物史观', '社会存在与社会意识、人民群众是历史的创造者、人生价值', '选择题'),
        ('公共基础知识', '毛泽东思想', '新民主主义革命理论、社会主义改造理论、党的建设', '选择题'),
        ('公共基础知识', '中国特色社会主义-邓小平理论', '社会主义本质、改革开放、社会主义市场经济', '选择题'),
        ('公共基础知识', '中国特色社会主义-三个代表', '代表先进生产力、先进文化、最广大人民根本利益', '选择题'),
        ('公共基础知识', '中国特色社会主义-科学发展观', '以人为本、全面协调可持续、统筹兼顾', '选择题'),
        ('公共基础知识', '中国特色社会主义-习近平新时代中国特色社会主义思想', '八个明确、十四个坚持、中国梦、人类命运共同体', '选择题'),
        ('公共基础知识', '宪法', '国家性质、国家机构、公民基本权利和义务、宪法修改', '选择题'),
        ('公共基础知识', '行政法', '行政行为、行政复议、行政诉讼、行政许可', '选择题'),
        ('公共基础知识', '民法', '民事主体、民事权利、合同、侵权责任、婚姻家庭', '选择题'),
        ('公共基础知识', '刑法', '犯罪构成、正当防卫、刑罚、常见罪名', '选择题'),
        ('公共基础知识', '微观经济', '供给与需求、市场结构、消费者行为、生产者行为', '选择题'),
        ('公共基础知识', '宏观经济', 'GDP、CPI、财政政策、货币政策、国际贸易', '选择题'),
        ('公共基础知识', '国际经济', '汇率、国际贸易、经济全球化、国际组织', '选择题'),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO civil_exam (subject,topic,content,question_type) VALUES (?,?,?,?)",
        topics
    )


def seed_couple_stories(conn):
    if conn.execute("SELECT COUNT(*) FROM couple_stories").fetchone()[0] >= 1:
        return
    stories = [
        ("我们的第一次旅行","那是一个阳光明媚的春天，我们一起去了海边。海风轻拂，浪花拍打着沙滩，我们在夕阳下牵手漫步。那一刻，我知道你就是我要找的人。","💕"),
        ("一起做饭的周末","每个周末我们都会一起做饭。你切菜，我掌勺，虽然有时候会手忙脚乱，但那些欢声笑语是最珍贵的回忆。","🍳"),
        ("雨中的温暖","那天突然下起了大雨，你冒着雨给我送伞。看到你全身湿透却还笑着说没事的时候，我的心都融化了。","☔"),
    ]
    conn.executemany(
        "INSERT OR IGNORE INTO couple_stories (title,content,mood) VALUES (?,?,?)",
        stories
    )
