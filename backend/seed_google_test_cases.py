import json
import textwrap
from pathlib import Path

from sqlalchemy import delete, select

from app.database import SessionLocal, initialize_database
from app.models import Playlist, PlaylistProblem, Problem, ProblemExecutionSpec, ProblemReferenceSolution, ProblemTestCase

ROOT = Path(__file__).resolve().parent
GOOGLE_TOP_50 = [
    1, 2, 3, 4, 8, 12, 14, 16, 18, 20, 28, 33, 41, 42, 44, 45, 48, 49, 52, 53,
    55, 57, 59, 64, 65, 67, 68, 74, 77, 82, 85, 87, 89, 90, 100, 101, 107, 111,
    114, 116, 118, 128, 133, 136, 138, 145, 147, 152, 154, 157,
]


def human_title(problem_id: int) -> str:
    csv_path = ROOT / "leetcode-companywise-interview-questions" / "google" / "all.csv"
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        for row in __import__("csv").DictReader(csv_file):
            if int(row["ID"]) == problem_id:
                return row["Title"]
    raise KeyError(problem_id)


def json_payload(value):
    return json.dumps(value, separators=(",", ":"))


def ensure_problem_support(problem_id: int, function_name: str, starter_code: str, source_code: str, test_cases: list[dict]):
    initialize_database()
    with SessionLocal() as db:
        problem = db.scalar(select(Problem).where(Problem.leetcode_id == problem_id))
        if problem is None:
            raise RuntimeError(f"Google problem {problem_id} is not imported; run import_google_playlist first.")

        spec = db.scalar(
            select(ProblemExecutionSpec).where(
                ProblemExecutionSpec.problem_id == problem.id,
                ProblemExecutionSpec.language == "python",
            )
        )
        if spec is None:
            spec = ProblemExecutionSpec(
                problem_id=problem.id,
                language="python",
                execution_type="function",
                function_name=function_name,
                starter_code=starter_code,
                input_format="JSON object with args and optional kwargs",
                output_format="JSON serializable output",
                output_comparison="exact_json",
            )
            db.add(spec)
        else:
            spec.execution_type = "function"
            spec.function_name = function_name
            spec.starter_code = starter_code
            spec.input_format = "JSON object with args and optional kwargs"
            spec.output_format = "JSON serializable output"
            spec.output_comparison = "exact_json"

        reference = db.scalar(
            select(ProblemReferenceSolution).where(
                ProblemReferenceSolution.problem_id == problem.id,
                ProblemReferenceSolution.language == "python",
            )
        )
        if reference is None:
            db.add(ProblemReferenceSolution(problem_id=problem.id, language="python", source_code=source_code))
        else:
            reference.source_code = source_code

        db.execute(delete(ProblemTestCase).where(ProblemTestCase.problem_id == problem.id))
        for position, test_case in enumerate(test_cases, start=1):
            db.add(
                ProblemTestCase(
                    problem_id=problem.id,
                    input_data=json_payload(test_case["input_data"]),
                    expected_output=json_payload(test_case["expected_output"]),
                    category=test_case.get("category", "custom"),
                    difficulty_level=test_case.get("difficulty_level", "medium"),
                    explanation=test_case.get("explanation", ""),
                    is_sample=test_case.get("is_sample", False),
                    position=position,
                )
            )
        db.commit()
        return len(test_cases)


def google_playlist_problem_ids() -> list[int]:
    initialize_database()
    with SessionLocal() as db:
        playlist = db.scalar(select(Playlist).where(Playlist.slug == "google"))
        if playlist is None:
            return []
        rows = db.execute(
            select(Problem.leetcode_id)
            .join(PlaylistProblem, PlaylistProblem.problem_id == Problem.id)
            .where(PlaylistProblem.playlist_id == playlist.id)
            .order_by(PlaylistProblem.position)
        ).scalars().all()
        return [int(value) for value in rows]


def seed_google_problem_support() -> int:
    problem_specs = {
        1: {
            "function_name": "twoSum",
            "starter_code": "def twoSum(nums, target):\n    return []",
            "source_code": textwrap.dedent('''
                def twoSum(nums, target):
                    seen = {}
                    for index, value in enumerate(nums):
                        complement = target - value
                        if complement in seen:
                            return [seen[complement], index]
                        seen[value] = index
                    return []
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 7, 11, 15], 9], "kwargs": {}}, "expected_output": [0, 1], "category": "normal", "difficulty_level": "easy", "explanation": "Plain example.", "is_sample": True},
                {"input_data": {"args": [[3, 2, 4], 6], "kwargs": {}}, "expected_output": [1, 2], "category": "normal", "difficulty_level": "easy", "explanation": "Complement appears later.", "is_sample": False},
                {"input_data": {"args": [[3, 3], 6], "kwargs": {}}, "expected_output": [0, 1], "category": "duplicate_values", "difficulty_level": "easy", "explanation": "Duplicate values can still form the pair.", "is_sample": False},
                {"input_data": {"args": [[-3, 4, 3, 90], 0], "kwargs": {}}, "expected_output": [0, 2], "category": "mixed_signs", "difficulty_level": "medium", "explanation": "A negative and a positive value can cancel.", "is_sample": False},
                {"input_data": {"args": [[1, 2], 100], "kwargs": {}}, "expected_output": [], "category": "no_solution", "difficulty_level": "medium", "explanation": "No pair sums to the target.", "is_sample": False},
            ],
        },
        2: {
            "function_name": "addTwoNumbers",
            "starter_code": "def addTwoNumbers(l1, l2):\n    return []",
            "source_code": textwrap.dedent('''
                def addTwoNumbers(l1, l2):
                    carry = 0
                    result = []
                    i = 0
                    while i < len(l1) or i < len(l2) or carry:
                        total = carry
                        if i < len(l1):
                            total += l1[i]
                        if i < len(l2):
                            total += l2[i]
                        result.append(total % 10)
                        carry = total // 10
                        i += 1
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 4, 3], [5, 6, 4]], "kwargs": {}}, "expected_output": [7, 0, 8], "category": "normal", "difficulty_level": "medium", "explanation": "Regular addition with carry.", "is_sample": True},
                {"input_data": {"args": [[9, 9, 9], [9, 9, 9]], "kwargs": {}}, "expected_output": [8, 9, 9, 1], "category": "carry", "difficulty_level": "medium", "explanation": "Long carry chain.", "is_sample": False},
                {"input_data": {"args": [[0], [0]], "kwargs": {}}, "expected_output": [0], "category": "zero", "difficulty_level": "easy", "explanation": "Zero inputs.", "is_sample": False},
            ],
        },
        3: {
            "function_name": "lengthOfLongestSubstring",
            "starter_code": "def lengthOfLongestSubstring(s):\n    return 0",
            "source_code": textwrap.dedent('''
                def lengthOfLongestSubstring(s):
                    left = 0
                    best = 0
                    seen = {}
                    for right, ch in enumerate(s):
                        if ch in seen and seen[ch] >= left:
                            left = seen[ch] + 1
                        seen[ch] = right
                        best = max(best, right - left + 1)
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["abcabcbb"], "kwargs": {}}, "expected_output": 3, "category": "normal", "difficulty_level": "medium", "explanation": "Longest substring without duplicates.", "is_sample": True},
                {"input_data": {"args": ["bbbbb"], "kwargs": {}}, "expected_output": 1, "category": "duplicate_run", "difficulty_level": "easy", "explanation": "All characters repeat.", "is_sample": False},
                {"input_data": {"args": ["pwwkew"], "kwargs": {}}, "expected_output": 3, "category": "mixed", "difficulty_level": "medium", "explanation": "Longest window with a repeated character in the middle.", "is_sample": False},
            ],
        },
        4: {
            "function_name": "findMedianSortedArrays",
            "starter_code": "def findMedianSortedArrays(nums1, nums2):\n    return 0.0",
            "source_code": textwrap.dedent('''
                def findMedianSortedArrays(nums1, nums2):
                    merged = sorted(nums1 + nums2)
                    n = len(merged)
                    if n % 2 == 0:
                        return (merged[n // 2 - 1] + merged[n // 2]) / 2.0
                    return float(merged[n // 2])
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 3], [2]], "kwargs": {}}, "expected_output": 2.0, "category": "normal", "difficulty_level": "hard", "explanation": "Even-length merge with singleton second input.", "is_sample": True},
                {"input_data": {"args": [[1, 2], [3, 4]], "kwargs": {}}, "expected_output": 2.5, "category": "even_length", "difficulty_level": "hard", "explanation": "Two sorted arrays of equal lengths.", "is_sample": False},
                {"input_data": {"args": [[0, 0], [0, 0]], "kwargs": {}}, "expected_output": 0.0, "category": "duplicate_zeroes", "difficulty_level": "medium", "explanation": "All zeros.", "is_sample": False},
            ],
        },
        8: {
            "function_name": "myAtoi",
            "starter_code": "def myAtoi(s):\n    return 0",
            "source_code": textwrap.dedent('''
                def myAtoi(s):
                    s = s.strip()
                    if not s:
                        return 0
                    sign = 1
                    if s[0] in '+-':
                        sign = -1 if s[0] == '-' else 1
                        s = s[1:]
                    digits = []
                    for ch in s:
                        if ch.isdigit():
                            digits.append(ch)
                        else:
                            break
                    if not digits:
                        return 0
                    value = int(''.join(digits)) * sign
                    if value < -2**31:
                        return -2**31
                    if value > 2**31 - 1:
                        return 2**31 - 1
                    return value
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["42"], "kwargs": {}}, "expected_output": 42, "category": "normal", "difficulty_level": "medium", "explanation": "Simple positive integer.", "is_sample": True},
                {"input_data": {"args": ["   -42"], "kwargs": {}}, "expected_output": -42, "category": "signed", "difficulty_level": "medium", "explanation": "Leading spaces and minus sign.", "is_sample": False},
                {"input_data": {"args": ["4193 with words"], "kwargs": {}}, "expected_output": 4193, "category": "trailing_text", "difficulty_level": "medium", "explanation": "Numeric prefix before letters.", "is_sample": False},
                {"input_data": {"args": ["9223372036854775808"], "kwargs": {}}, "expected_output": 2147483647, "category": "overflow", "difficulty_level": "hard", "explanation": "Clamp to 32-bit range.", "is_sample": False},
            ],
        },
        12: {
            "function_name": "intToRoman",
            "starter_code": "def intToRoman(num):\n    return ''",
            "source_code": textwrap.dedent('''
                def intToRoman(num):
                    values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
                    symbols = ['M', 'CM', 'D', 'CD', 'C', 'XC', 'L', 'XL', 'X', 'IX', 'V', 'IV', 'I']
                    result = []
                    for value, symbol in zip(values, symbols):
                        count, num = divmod(num, value)
                        result.append(symbol * count)
                    return ''.join(result)
            ''').strip(),
            "tests": [
                {"input_data": {"args": [3], "kwargs": {}}, "expected_output": "III", "category": "normal", "difficulty_level": "medium", "explanation": "Basic Roman numeral.", "is_sample": True},
                {"input_data": {"args": [58], "kwargs": {}}, "expected_output": "LVIII", "category": "mixed_value", "difficulty_level": "medium", "explanation": "Composite value with subtraction rules.", "is_sample": False},
                {"input_data": {"args": [1994], "kwargs": {}}, "expected_output": "MCMXCIV", "category": "subtractive", "difficulty_level": "hard", "explanation": "Subtractive notation across place values.", "is_sample": False},
            ],
        },
        14: {
            "function_name": "longestCommonPrefix",
            "starter_code": "def longestCommonPrefix(strs):\n    return ''",
            "source_code": textwrap.dedent('''
                def longestCommonPrefix(strs):
                    if not strs:
                        return ''
                    prefix = strs[0]
                    for word in strs[1:]:
                        while not word.startswith(prefix):
                            prefix = prefix[:-1]
                            if not prefix:
                                return ''
                    return prefix
            ''').strip(),
            "tests": [
                {"input_data": {"args": [["flower", "flow", "flight"]], "kwargs": {}}, "expected_output": "fl", "category": "normal", "difficulty_level": "easy", "explanation": "Common prefix across strings.", "is_sample": True},
                {"input_data": {"args": [["dog", "racecar", "car"]], "kwargs": {}}, "expected_output": "", "category": "no_prefix", "difficulty_level": "easy", "explanation": "No common prefix.", "is_sample": False},
            ],
        },
        16: {
            "function_name": "threeSumClosest",
            "starter_code": "def threeSumClosest(nums, target):\n    return 0",
            "source_code": textwrap.dedent('''
                def threeSumClosest(nums, target):
                    nums.sort()
                    best = sum(nums[:3])
                    for i in range(len(nums) - 2):
                        left, right = i + 1, len(nums) - 1
                        while left < right:
                            total = nums[i] + nums[left] + nums[right]
                            if abs(total - target) < abs(best - target):
                                best = total
                            if total < target:
                                left += 1
                            elif total > target:
                                right -= 1
                            else:
                                return target
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[-1, 2, 1, -4], 1], "kwargs": {}}, "expected_output": 2, "category": "normal", "difficulty_level": "medium", "explanation": "Nearest triplet to the target.", "is_sample": True},
                {"input_data": {"args": [[0, 0, 0], 1], "kwargs": {}}, "expected_output": 0, "category": "all_zeroes", "difficulty_level": "easy", "explanation": "Triplet sum exactly zero.", "is_sample": False},
            ],
        },
        18: {
            "function_name": "fourSum",
            "starter_code": "def fourSum(nums, target):\n    return []",
            "source_code": textwrap.dedent('''
                def fourSum(nums, target):
                    nums.sort()
                    results = []
                    n = len(nums)
                    for i in range(n - 3):
                        if i > 0 and nums[i] == nums[i - 1]:
                            continue
                        for j in range(i + 1, n - 2):
                            if j > i + 1 and nums[j] == nums[j - 1]:
                                continue
                            left, right = j + 1, n - 1
                            while left < right:
                                total = nums[i] + nums[j] + nums[left] + nums[right]
                                if total == target:
                                    results.append([nums[i], nums[j], nums[left], nums[right]])
                                    left += 1
                                    right -= 1
                                    while left < right and nums[left] == nums[left - 1]:
                                        left += 1
                                    while left < right and nums[right] == nums[right + 1]:
                                        right -= 1
                                elif total < target:
                                    left += 1
                                else:
                                    right -= 1
                    return results
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 0, -1, 0, -2, 2], 0], "kwargs": {}}, "expected_output": [[-2, -1, 1, 2], [-2, 0, 0, 2], [-1, 0, 0, 1]], "category": "normal", "difficulty_level": "medium", "explanation": "Four numbers sum to target.", "is_sample": True},
                {"input_data": {"args": [[2, 2, 2, 2], 8], "kwargs": {}}, "expected_output": [[2, 2, 2, 2]], "category": "duplicate_values", "difficulty_level": "easy", "explanation": "Repeated values still form a valid quadruplet.", "is_sample": False},
            ],
        },
        20: {
            "function_name": "isValid",
            "starter_code": "def isValid(s):\n    return False",
            "source_code": textwrap.dedent('''
                def isValid(s):
                    stack = []
                    pairs = {')': '(', ']': '[', '}': '{'}
                    for ch in s:
                        if ch in '([{':
                            stack.append(ch)
                        elif not stack or pairs[ch] != stack.pop():
                            return False
                    return not stack
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["()[]{}"], "kwargs": {}}, "expected_output": True, "category": "normal", "difficulty_level": "easy", "explanation": "Balanced brackets.", "is_sample": True},
                {"input_data": {"args": ["(]"], "kwargs": {}}, "expected_output": False, "category": "mismatch", "difficulty_level": "easy", "explanation": "Wrong closing bracket order.", "is_sample": False},
            ],
        },
        28: {
            "function_name": "strStr",
            "starter_code": "def strStr(haystack, needle):\n    return -1",
            "source_code": textwrap.dedent('''
                def strStr(haystack, needle):
                    if needle == '':
                        return 0
                    pos = haystack.find(needle)
                    return pos if pos != -1 else -1
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["sadbutsad", "sad"]}, "expected_output": 0, "category": "normal", "difficulty_level": "easy", "explanation": "Find needle at the beginning.", "is_sample": True},
                {"input_data": {"args": ["leetcode", "leeto"]}, "expected_output": -1, "category": "missing", "difficulty_level": "easy", "explanation": "Needle is absent.", "is_sample": False},
            ],
        },
        33: {
            "function_name": "search",
            "starter_code": "def search(nums, target):\n    return -1",
            "source_code": textwrap.dedent('''
                def search(nums, target):
                    left, right = 0, len(nums) - 1
                    while left <= right:
                        mid = (left + right) // 2
                        if nums[mid] == target:
                            return mid
                        if nums[left] <= nums[mid]:
                            if nums[left] <= target < nums[mid]:
                                right = mid - 1
                            else:
                                left = mid + 1
                        else:
                            if nums[mid] < target <= nums[right]:
                                left = mid + 1
                            else:
                                right = mid - 1
                    return -1
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[4, 5, 6, 7, 0, 1, 2], 0], "kwargs": {}}, "expected_output": 4, "category": "normal", "difficulty_level": "medium", "explanation": "Target appears in the rotated segment.", "is_sample": True},
                {"input_data": {"args": [[4, 5, 6, 7, 0, 1, 2], 3], "kwargs": {}}, "expected_output": -1, "category": "missing", "difficulty_level": "easy", "explanation": "Target is absent.", "is_sample": False},
            ],
        },
        41: {
            "function_name": "firstMissingPositive",
            "starter_code": "def firstMissingPositive(nums):\n    return 1",
            "source_code": textwrap.dedent('''
                def firstMissingPositive(nums):
                    n = len(nums)
                    for i in range(n):
                        while 1 <= nums[i] <= n and nums[nums[i] - 1] != nums[i]:
                            nums[nums[i] - 1], nums[i] = nums[i], nums[nums[i] - 1]
                    for i in range(n):
                        if nums[i] != i + 1:
                            return i + 1
                    return n + 1
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 2, 0]], "kwargs": {}}, "expected_output": 3, "category": "normal", "difficulty_level": "hard", "explanation": "Smallest missing positive integer.", "is_sample": True},
                {"input_data": {"args": [[3, 4, -1, 1]], "kwargs": {}}, "expected_output": 2, "category": "negative_values", "difficulty_level": "hard", "explanation": "Negative and duplicated values are present.", "is_sample": False},
            ],
        },
        42: {
            "function_name": "trap",
            "starter_code": "def trap(height):\n    return 0",
            "source_code": textwrap.dedent('''
                def trap(height):
                    if not height:
                        return 0
                    left, right = 0, len(height) - 1
                    left_max = right_max = 0
                    trapped = 0
                    while left <= right:
                        if height[left] <= height[right]:
                            if height[left] >= left_max:
                                left_max = height[left]
                            else:
                                trapped += left_max - height[left]
                            left += 1
                        else:
                            if height[right] >= right_max:
                                right_max = height[right]
                            else:
                                trapped += right_max - height[right]
                            right -= 1
                    return trapped
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[0, 1, 0, 2, 0, 3, 0, 4, 0, 1]], "kwargs": {}}, "expected_output": 7, "category": "normal", "difficulty_level": "hard", "explanation": "Classic trapping rain water example.", "is_sample": True},
                {"input_data": {"args": [[4, 2, 0, 3, 2, 5]], "kwargs": {}}, "expected_output": 9, "category": "mixed", "difficulty_level": "hard", "explanation": "Multiple level differences across the span.", "is_sample": False},
            ],
        },
        44: {
            "function_name": "isMatch",
            "starter_code": "def isMatch(s, p):\n    return False",
            "source_code": textwrap.dedent('''
                def isMatch(s, p):
                    memo = {}
                    def dp(i, j):
                        key = (i, j)
                        if key in memo:
                            return memo[key]
                        if j == len(p):
                            result = i == len(s)
                        elif p[j] == '*':
                            result = dp(i, j + 1) or (i < len(s) and (s[i] == p[j - 1] or p[j - 1] == '?') and dp(i + 1, j))
                        else:
                            result = i < len(s) and (s[i] == p[j] or p[j] == '?') and dp(i + 1, j + 1)
                        memo[key] = result
                        return result
                    return dp(0, 0)
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["aa", "a"]}, "expected_output": False, "category": "single_char", "difficulty_level": "hard", "explanation": "Single-character wildcard pattern should not match repeated chars.", "is_sample": True},
                {"input_data": {"args": ["cb", "?a"]}, "expected_output": False, "category": "question_mark", "difficulty_level": "hard", "explanation": "One wildcard can match one character only.", "is_sample": False},
            ],
        },
        45: {
            "function_name": "jump",
            "starter_code": "def jump(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def jump(nums):
                    steps = 0
                    farthest = 0
                    end = 0
                    for i in range(len(nums) - 1):
                        farthest = max(farthest, i + nums[i])
                        if i == end:
                            steps += 1
                            end = farthest
                    return steps
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 3, 1, 1, 4]], "kwargs": {}}, "expected_output": 2, "category": "normal", "difficulty_level": "medium", "explanation": "Minimum jumps to the end.", "is_sample": True},
                {"input_data": {"args": [[1, 2, 3]], "kwargs": {}}, "expected_output": 2, "category": "linear", "difficulty_level": "easy", "explanation": "Straightforward progression.", "is_sample": False},
            ],
        },
        48: {
            "function_name": "rotate",
            "starter_code": "def rotate(matrix):\n    return []",
            "source_code": textwrap.dedent('''
                def rotate(matrix):
                    n = len(matrix)
                    for layer in range(n // 2):
                        for i in range(layer, n - layer - 1):
                            temp = matrix[layer][i]
                            matrix[layer][i] = matrix[n - 1 - i][layer]
                            matrix[n - 1 - i][layer] = matrix[n - 1 - layer][n - 1 - i]
                            matrix[n - 1 - layer][n - 1 - i] = matrix[i][n - 1 - layer]
                            matrix[i][n - 1 - layer] = temp
                    return matrix
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[[1, 2, 3], [4, 5, 6], [7, 8, 9]]], "kwargs": {}}, "expected_output": [[7, 4, 1], [8, 5, 2], [9, 6, 3]], "category": "normal", "difficulty_level": "medium", "explanation": "90-degree clockwise rotation.", "is_sample": True},
                {"input_data": {"args": [[[5, 1], [9, 7]]], "kwargs": {}}, "expected_output": [[9, 5], [7, 1]], "category": "2x2", "difficulty_level": "easy", "explanation": "Small square matrix.", "is_sample": False},
            ],
        },
        49: {
            "function_name": "groupAnagrams",
            "starter_code": "def groupAnagrams(strs):\n    return []",
            "source_code": textwrap.dedent('''
                def groupAnagrams(strs):
                    groups = {}
                    for s in strs:
                        key = ''.join(sorted(s))
                        groups.setdefault(key, []).append(s)
                    return [value for value in groups.values()]
            ''').strip(),
            "tests": [
                {"input_data": {"args": [["eat", "tea", "tan", "ate", "nat", "bat"]], "kwargs": {}}, "expected_output": [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]], "category": "normal", "difficulty_level": "medium", "explanation": "Group anagrams by sorted-letter signature.", "is_sample": True},
                {"input_data": {"args": [[""], [""], ["a"]], "kwargs": {}}, "expected_output": [[""], [""], ["a"]], "category": "empty_and_single", "difficulty_level": "easy", "explanation": "Empty string and single-character strings still group correctly.", "is_sample": False},
            ],
        },
        52: {
            "function_name": "totalNQueens",
            "starter_code": "def totalNQueens(n):\n    return 0",
            "source_code": textwrap.dedent('''
                def totalNQueens(n):
                    cols = set()
                    pos_diag = set()
                    neg_diag = set()
                    count = [0]
                    def backtrack(row):
                        if row == n:
                            count[0] += 1
                            return
                        for col in range(n):
                            if col in cols or (row - col) in pos_diag or (row + col) in neg_diag:
                                continue
                            cols.add(col)
                            pos_diag.add(row - col)
                            neg_diag.add(row + col)
                            backtrack(row + 1)
                            neg_diag.remove(row + col)
                            pos_diag.remove(row - col)
                            cols.remove(col)
                    backtrack(0)
                    return count[0]
            ''').strip(),
            "tests": [
                {"input_data": {"args": [4], "kwargs": {}}, "expected_output": 2, "category": "normal", "difficulty_level": "hard", "explanation": "Four-queen arrangement count.", "is_sample": True},
                {"input_data": {"args": [1], "kwargs": {}}, "expected_output": 1, "category": "single", "difficulty_level": "easy", "explanation": "Single queen has one arrangement.", "is_sample": False},
            ],
        },
        53: {
            "function_name": "maxSubArray",
            "starter_code": "def maxSubArray(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def maxSubArray(nums):
                    current = best = nums[0]
                    for value in nums[1:]:
                        current = max(value, current + value)
                        best = max(best, current)
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "kwargs": {}}, "expected_output": 6, "category": "normal", "difficulty_level": "medium", "explanation": "Maximum subarray sum.", "is_sample": True},
                {"input_data": {"args": [[1]], "kwargs": {}}, "expected_output": 1, "category": "single", "difficulty_level": "easy", "explanation": "Single-item array.", "is_sample": False},
            ],
        },
        55: {
            "function_name": "canJump",
            "starter_code": "def canJump(nums):\n    return False",
            "source_code": textwrap.dedent('''
                def canJump(nums):
                    farthest = 0
                    for index, value in enumerate(nums):
                        if index > farthest:
                            return False
                        farthest = max(farthest, index + value)
                        if farthest >= len(nums) - 1:
                            return True
                    return farthest >= len(nums) - 1
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 3, 1, 1, 4]], "kwargs": {}}, "expected_output": True, "category": "normal", "difficulty_level": "medium", "explanation": "Reach the last index using the jumps.", "is_sample": True},
                {"input_data": {"args": [[3, 2, 1, 0, 4]], "kwargs": {}}, "expected_output": False, "category": "blocked", "difficulty_level": "medium", "explanation": "A zero blocks the path.", "is_sample": False},
            ],
        },
        57: {
            "function_name": "insert",
            "starter_code": "def insert(intervals, newInterval):\n    return []",
            "source_code": textwrap.dedent('''
                def insert(intervals, newInterval):
                    intervals = [list(interval) for interval in intervals]
                    intervals.append(newInterval)
                    intervals.sort()
                    merged = []
                    for current in intervals:
                        if not merged or current[0] > merged[-1][1]:
                            merged.append(current)
                        else:
                            merged[-1][1] = max(merged[-1][1], current[1])
                    return merged
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[[1, 3], [6, 9]], [2, 5]], "kwargs": {}}, "expected_output": [[1, 5], [6, 9]], "category": "normal", "difficulty_level": "medium", "explanation": "Insert interval overlaps existing ranges.", "is_sample": True},
                {"input_data": {"args": [[[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8]], "kwargs": {}}, "expected_output": [[1, 2], [3, 10], [12, 16]], "category": "merge_chain", "difficulty_level": "medium", "explanation": "Multiple overlapping intervals.", "is_sample": False},
            ],
        },
        59: {
            "function_name": "generateMatrix",
            "starter_code": "def generateMatrix(n):\n    return []",
            "source_code": textwrap.dedent('''
                def generateMatrix(n):
                    matrix = [[0] * n for _ in range(n)]
                    top, bottom = 0, n - 1
                    left, right = 0, n - 1
                    value = 1
                    while top <= bottom and left <= right:
                        for col in range(left, right + 1):
                            matrix[top][col] = value; value += 1
                        top += 1
                        for row in range(top, bottom + 1):
                            matrix[row][right] = value; value += 1
                        right -= 1
                        if top <= bottom:
                            for col in range(right, left - 1, -1):
                                matrix[bottom][col] = value; value += 1
                            bottom -= 1
                        if left <= right:
                            for row in range(bottom, top - 1, -1):
                                matrix[row][left] = value; value += 1
                            left += 1
                    return matrix
            ''').strip(),
            "tests": [
                {"input_data": {"args": [3], "kwargs": {}}, "expected_output": [[1, 2, 3], [8, 9, 4], [7, 6, 5]], "category": "normal", "difficulty_level": "medium", "explanation": "Classic spiral fill of a 3x3 matrix.", "is_sample": True},
                {"input_data": {"args": [1], "kwargs": {}}, "expected_output": [[1]], "category": "single", "difficulty_level": "easy", "explanation": "Single-cell output.", "is_sample": False},
            ],
        },
        64: {
            "function_name": "minPathSum",
            "starter_code": "def minPathSum(grid):\n    return 0",
            "source_code": textwrap.dedent('''
                def minPathSum(grid):
                    rows, cols = len(grid), len(grid[0])
                    dp = [[0] * cols for _ in range(rows)]
                    dp[0][0] = grid[0][0]
                    for r in range(1, rows):
                        dp[r][0] = dp[r - 1][0] + grid[r][0]
                    for c in range(1, cols):
                        dp[0][c] = dp[0][c - 1] + grid[0][c]
                    for r in range(1, rows):
                        for c in range(1, cols):
                            dp[r][c] = min(dp[r - 1][c], dp[r][c - 1]) + grid[r][c]
                    return dp[-1][-1]
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[ [1, 3, 1], [1, 5, 1], [4, 2, 1] ]]}, "expected_output": 7, "category": "normal", "difficulty_level": "medium", "explanation": "Minimum cost from top-left to bottom-right.", "is_sample": True},
                {"input_data": {"args": [[[1, 2], [1, 1]]], "kwargs": {}}, "expected_output": 4, "category": "2x2", "difficulty_level": "easy", "explanation": "A compact path across a 2x2 grid.", "is_sample": False},
            ],
        },
        65: {
            "function_name": "isNumber",
            "starter_code": "def isNumber(s):\n    return False",
            "source_code": textwrap.dedent('''
                def isNumber(s):
                    s = s.strip()
                    if not s:
                        return False
                    seen_digit = False
                    seen_dot = False
                    seen_exp = False
                    for i, ch in enumerate(s):
                        if ch.isdigit():
                            seen_digit = True
                        elif ch in '+-':
                            if i != 0 and s[i - 1] not in 'eE':
                                return False
                        elif ch == '.':
                            if seen_dot or seen_exp:
                                return False
                            seen_dot = True
                        elif ch in 'eE':
                            if seen_exp or not seen_digit:
                                return False
                            seen_exp = True
                            seen_digit = False
                        else:
                            return False
                    return seen_digit
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["0"], "kwargs": {}}, "expected_output": True, "category": "plain_int", "difficulty_level": "medium", "explanation": "Simple integer literal.", "is_sample": True},
                {"input_data": {"args": ["e9"], "kwargs": {}}, "expected_output": False, "category": "invalid_exponent", "difficulty_level": "hard", "explanation": "Exponent without a leading numeric token is invalid.", "is_sample": False},
                {"input_data": {"args": ["6e-1"], "kwargs": {}}, "expected_output": True, "category": "scientific", "difficulty_level": "hard", "explanation": "Valid scientific notation.", "is_sample": False},
            ],
        },
        67: {
            "function_name": "addBinary",
            "starter_code": "def addBinary(a, b):\n    return ''",
            "source_code": textwrap.dedent('''
                def addBinary(a, b):
                    i = len(a) - 1
                    j = len(b) - 1
                    carry = 0
                    result = []
                    while i >= 0 or j >= 0 or carry:
                        total = carry
                        if i >= 0:
                            total += int(a[i])
                            i -= 1
                        if j >= 0:
                            total += int(b[j])
                            j -= 1
                        result.append(str(total % 2))
                        carry = total // 2
                    return ''.join(reversed(result))
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["11", "1"]}, "expected_output": "100", "category": "normal", "difficulty_level": "easy", "explanation": "Binary addition with carry.", "is_sample": True},
                {"input_data": {"args": ["1010", "1011"]}, "expected_output": "10101", "category": "carry_chain", "difficulty_level": "medium", "explanation": "Multiple carry positions.", "is_sample": False},
            ],
        },
        68: {
            "function_name": "fullJustify",
            "starter_code": "def fullJustify(words, maxWidth):\n    return []",
            "source_code": textwrap.dedent('''
                def fullJustify(words, maxWidth):
                    lines = []
                    current = []
                    current_length = 0
                    for word in words:
                        if not current:
                            current = [word]
                            current_length = len(word)
                        elif current_length + 1 + len(word) <= maxWidth:
                            current.append(word)
                            current_length += 1 + len(word)
                        else:
                            lines.append(current)
                            current = [word]
                            current_length = len(word)
                    if current:
                        lines.append(current)
                    result = []
                    for idx, line in enumerate(lines):
                        if idx == len(lines) - 1 or len(line) == 1:
                            text = ' '.join(line)
                            result.append(text + ' ' * (maxWidth - len(text)))
                        else:
                            total_chars = sum(len(word) for word in line)
                            spaces = maxWidth - total_chars
                            gaps = len(line) - 1
                            base = spaces // gaps
                            extra = spaces % gaps
                            pieces = []
                            for pos, word in enumerate(line):
                                pieces.append(word)
                                if pos != len(line) - 1:
                                    pieces.append(' ' * (base + (1 if pos < extra else 0)))
                            result.append(''.join(pieces))
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [["This", "is", "an", "example", "of", "text", "justification."], 16], "kwargs": {}}, "expected_output": ["This    is    an", "example  of text", "justification.  "], "category": "normal", "difficulty_level": "hard", "explanation": "Text lines are justified to a fixed width.", "is_sample": True},
                {"input_data": {"args": [["What", "must", "be", "acknowledgment", "shall", "be"], 16], "kwargs": {}}, "expected_output": ["What   must   be", "acknowledgment  ", "shall be        "], "category": "edge_spacing", "difficulty_level": "hard", "explanation": "Spacing must handle unequal word counts and trailing spaces.", "is_sample": False},
            ],
        },
        74: {
            "function_name": "searchMatrix",
            "starter_code": "def searchMatrix(matrix, target):\n    return False",
            "source_code": textwrap.dedent('''
                def searchMatrix(matrix, target):
                    if not matrix or not matrix[0]:
                        return False
                    rows, cols = len(matrix), len(matrix[0])
                    left, right = 0, rows * cols - 1
                    while left <= right:
                        mid = (left + right) // 2
                        value = matrix[mid // cols][mid % cols]
                        if value == target:
                            return True
                        if value < target:
                            left = mid + 1
                        else:
                            right = mid - 1
                    return False
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3], "kwargs": {}}, "expected_output": True, "category": "normal", "difficulty_level": "medium", "explanation": "Search a sorted matrix efficiently.", "is_sample": True},
                {"input_data": {"args": [[[1]], 2], "kwargs": {}}, "expected_output": False, "category": "single_row", "difficulty_level": "easy", "explanation": "Only one row and one element.", "is_sample": False},
            ],
        },
        77: {
            "function_name": "combine",
            "starter_code": "def combine(n, k):\n    return []",
            "source_code": textwrap.dedent('''
                def combine(n, k):
                    if k <= 0 or k > n:
                        return []
                    result = []
                    def backtrack(start, current):
                        if len(current) == k:
                            result.append(current[:])
                            return
                        for value in range(start, n + 1):
                            current.append(value)
                            backtrack(value + 1, current)
                            current.pop()
                    backtrack(1, [])
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [4, 2], "kwargs": {}}, "expected_output": [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]], "category": "normal", "difficulty_level": "medium", "explanation": "All combinations of size 2 from 1..4.", "is_sample": True},
                {"input_data": {"args": [3, 1], "kwargs": {}}, "expected_output": [[1], [2], [3]], "category": "single_choice", "difficulty_level": "easy", "explanation": "Single-element combinations.", "is_sample": False},
            ],
        },
        82: {
            "function_name": "deleteDuplicates",
            "starter_code": "def deleteDuplicates(head):\n    return []",
            "source_code": textwrap.dedent('''
                def deleteDuplicates(head):
                    if not head:
                        return []
                    result = []
                    i = 0
                    while i < len(head):
                        if i + 1 < len(head) and head[i] == head[i + 1]:
                            while i + 1 < len(head) and head[i] == head[i + 1]:
                                i += 1
                            i += 1
                        else:
                            result.append(head[i])
                            i += 1
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 2, 3, 3, 4, 4, 5]], "kwargs": {}}, "expected_output": [1, 2, 5], "category": "normal", "difficulty_level": "medium", "explanation": "Remove all duplicates in a sorted list.", "is_sample": True},
                {"input_data": {"args": [[1, 1, 1]], "kwargs": {}}, "expected_output": [], "category": "all_duplicates", "difficulty_level": "easy", "explanation": "Every element repeats.", "is_sample": False},
            ],
        },
        85: {
            "function_name": "maximalRectangle",
            "starter_code": "def maximalRectangle(matrix):\n    return 0",
            "source_code": textwrap.dedent('''
                def maximalRectangle(matrix):
                    if not matrix or not matrix[0]:
                        return 0
                    rows, cols = len(matrix), len(matrix[0])
                    heights = [0] * cols
                    best = 0
                    for row in matrix:
                        for col in range(cols):
                            heights[col] = heights[col] + 1 if row[col] == '1' else 0
                        stack = []
                        for idx, value in enumerate(heights + [0]):
                            while stack and heights[stack[-1]] > value:
                                h = heights[stack.pop()]
                                w = idx - (stack[-1] if stack else 0) - 1
                                best = max(best, h * w)
                            stack.append(idx)
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": [["10100", "10111", "11111", "10010"]], "kwargs": {}}, "expected_output": 6, "category": "normal", "difficulty_level": "hard", "explanation": "Largest rectangle of ones inside the binary matrix.", "is_sample": True},
                {"input_data": {"args": [["0", "0"]], "kwargs": {}}, "expected_output": 0, "category": "empty", "difficulty_level": "easy", "explanation": "Matrix of zeros yields no rectangle.", "is_sample": False},
            ],
        },
        87: {
            "function_name": "isScramble",
            "starter_code": "def isScramble(s1, s2):\n    return False",
            "source_code": textwrap.dedent('''
                def isScramble(s1, s2):
                    if s1 == s2:
                        return True
                    if len(s1) != len(s2):
                        return False
                    if sorted(s1) != sorted(s2):
                        return False
                    n = len(s1)
                    for i in range(1, n):
                        if isScramble(s1[:i], s2[:i]) and isScramble(s1[i:], s2[i:]):
                            return True
                        if isScramble(s1[:i], s2[n - i:]) and isScramble(s1[i:], s2[:n - i]):
                            return True
                    return False
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["great", "rgeat"]}, "expected_output": True, "category": "normal", "difficulty_level": "hard", "explanation": "Scrambled string can be reconstructed by recursive swaps.", "is_sample": True},
                {"input_data": {"args": ["abc", "bca"]}, "expected_output": True, "category": "rearranged", "difficulty_level": "medium", "explanation": "Characters are the same but in a different order.", "is_sample": False},
                {"input_data": {"args": ["abc", "abd"]}, "expected_output": False, "category": "different", "difficulty_level": "easy", "explanation": "Different character sets cannot scramble to match.", "is_sample": False},
            ],
        },
        89: {
            "function_name": "grayCode",
            "starter_code": "def grayCode(n):\n    return []",
            "source_code": textwrap.dedent('''
                def grayCode(n):
                    result = [0]
                    for _ in range(n):
                        result += [value + (1 << _) for value in reversed(result)]
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [2], "kwargs": {}}, "expected_output": [0, 1, 3, 2], "category": "normal", "difficulty_level": "medium", "explanation": "Gray code sequence for n=2.", "is_sample": True},
                {"input_data": {"args": [0], "kwargs": {}}, "expected_output": [0], "category": "zero", "difficulty_level": "easy", "explanation": "Zero-bit Gray code is just [0].", "is_sample": False},
            ],
        },
        90: {
            "function_name": "subsetsWithDup",
            "starter_code": "def subsetsWithDup(nums):\n    return []",
            "source_code": textwrap.dedent('''
                def subsetsWithDup(nums):
                    nums.sort()
                    result = []
                    def backtrack(start, current):
                        result.append(current[:])
                        for i in range(start, len(nums)):
                            if i > start and nums[i] == nums[i - 1]:
                                continue
                            current.append(nums[i])
                            backtrack(i + 1, current)
                            current.pop()
                    backtrack(0, [])
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 2, 2]], "kwargs": {}}, "expected_output": [[ ], [1], [1, 2], [1, 2, 2], [2], [2, 2]], "category": "duplicates", "difficulty_level": "medium", "explanation": "Subsets of a list containing repeated values.", "is_sample": True},
                {"input_data": {"args": [[0]], "kwargs": {}}, "expected_output": [[ ], [0]], "category": "single", "difficulty_level": "easy", "explanation": "One-element subset generation.", "is_sample": False},
            ],
        },
        100: {
            "function_name": "isSameTree",
            "starter_code": "def isSameTree(p, q):\n    return False",
            "source_code": textwrap.dedent('''
                def isSameTree(p, q):
                    if p is None or q is None:
                        return p is None and q is None
                    if p[0] != q[0]:
                        return False
                    return isSameTree(p[1], q[1]) and isSameTree(p[2], q[2])
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, [2, None, None], [3, None, None]], [1, [2, None, None], [3, None, None]]], "kwargs": {}}, "expected_output": True, "category": "identical", "difficulty_level": "easy", "explanation": "Two identical trees are the same.", "is_sample": True},
                {"input_data": {"args": [[1, [2, None, None], None], [1, None, [2, None, None]]], "kwargs": {}}, "expected_output": False, "category": "different_structure", "difficulty_level": "easy", "explanation": "The same values are arranged differently.", "is_sample": False},
            ],
        },
        101: {
            "function_name": "isSymmetric",
            "starter_code": "def isSymmetric(root):\n    return False",
            "source_code": textwrap.dedent('''
                def isSymmetric(root):
                    def mirror(a, b):
                        if a is None or b is None:
                            return a is None and b is None
                        if a[0] != b[0]:
                            return False
                        return mirror(a[1], b[2]) and mirror(a[2], b[1])
                    return root is None or mirror(root[1], root[2])
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, [2, [3, None, None], [4, None, None]], [2, [4, None, None], [3, None, None]]]], "kwargs": {}}, "expected_output": True, "category": "mirror", "difficulty_level": "easy", "explanation": "Tree is symmetric around the root.", "is_sample": True},
                {"input_data": {"args": [[1, [2, None, None], [3, None, None]]], "kwargs": {}}, "expected_output": False, "category": "asymmetric", "difficulty_level": "easy", "explanation": "Left and right subtrees differ.", "is_sample": False},
            ],
        },
        107: {
            "function_name": "levelOrderBottom",
            "starter_code": "def levelOrderBottom(root):\n    return []",
            "source_code": textwrap.dedent('''
                def levelOrderBottom(root):
                    if root is None:
                        return []
                    levels = []
                    queue = [[root, 0]]
                    while queue:
                        node, depth = queue.pop(0)
                        if depth == len(levels):
                            levels.append([])
                        levels[depth].append(node[0])
                        if node[1] is not None: queue.append([node[1], depth + 1])
                        if node[2] is not None: queue.append([node[2], depth + 1])
                    return list(reversed(levels))
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[3, [9, None, None], [20, [15, None, None], [7, None, None]]]]}, "expected_output": [[15, 7], [9, 20], [3]], "category": "normal", "difficulty_level": "medium", "explanation": "Level-order traversal from bottom to top.", "is_sample": True},
                {"input_data": {"args": [[1, None, None]]}, "expected_output": [[1]], "category": "single_node", "difficulty_level": "easy", "explanation": "One-node tree.", "is_sample": False},
            ],
        },
        111: {
            "function_name": "minDepth",
            "starter_code": "def minDepth(root):\n    return 0",
            "source_code": textwrap.dedent('''
                def minDepth(root):
                    if root is None:
                        return 0
                    if root[1] is None and root[2] is None:
                        return 1
                    left = minDepth(root[1]) if root[1] is not None else float('inf')
                    right = minDepth(root[2]) if root[2] is not None else float('inf')
                    return 1 + min(left, right)
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[3, [9, None, None], [20, [15, None, None], [7, None, None]]]]}, "expected_output": 2, "category": "normal", "difficulty_level": "easy", "explanation": "Short root-to-leaf depth.", "is_sample": True},
                {"input_data": {"args": [[1, [2, None, None], None]]}, "expected_output": 2, "category": "left_only", "difficulty_level": "easy", "explanation": "Only one child branch exists.", "is_sample": False},
            ],
        },
        114: {
            "function_name": "flatten",
            "starter_code": "def flatten(root):\n    return None",
            "source_code": textwrap.dedent('''
                def flatten(root):
                    if root is None:
                        return None
                    left = root[1]
                    right = root[2]
                    flatten(left)
                    flatten(right)
                    if left is not None:
                        current = left
                        while current[2] is not None:
                            current = current[2]
                        current[2] = right
                        root[2] = left
                        root[1] = None
                    return root
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, [2, [3, None, None], [4, None, None]], [5, None, [6, None, None]]]]}, "expected_output": [1, [2, [3, None, None], [4, None, None]], [5, None, [6, None, None]]], "category": "normal", "difficulty_level": "medium", "explanation": "The tree is re-linked into a flat right-chain structure.", "is_sample": True},
            ],
        },
        116: {
            "function_name": "connect",
            "starter_code": "def connect(root):\n    return root",
            "source_code": textwrap.dedent('''
                def connect(root):
                    if root is None or root[1] is None and root[2] is None:
                        return root
                    if root[1] is not None:
                        root[1][3] = root[2] if root[2] is not None else None
                    if root[2] is not None:
                        root[2][3] = None
                    connect(root[1])
                    connect(root[2])
                    return root
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, [2, [4, None, None], [5, None, None]], [3, [6, None, None], [7, None, None]]]]}, "expected_output": [1, [2, [4, None, None], [5, None, None]], [3, [6, None, None], [7, None, None]]], "category": "normal", "difficulty_level": "medium", "explanation": "Return the tree with next pointers attached to siblings.", "is_sample": True},
            ],
        },
        118: {
            "function_name": "generate",
            "starter_code": "def generate(numRows):\n    return []",
            "source_code": textwrap.dedent('''
                def generate(numRows):
                    rows = []
                    for row in range(numRows):
                        current = [1] * (row + 1)
                        for i in range(1, row):
                            current[i] = rows[row - 1][i - 1] + rows[row - 1][i]
                        rows.append(current)
                    return rows
            ''').strip(),
            "tests": [
                {"input_data": {"args": [5], "kwargs": {}}, "expected_output": [[1], [1, 1], [1, 2, 1], [1, 3, 3, 1], [1, 4, 6, 4, 1]], "category": "normal", "difficulty_level": "easy", "explanation": "Pascal's triangle with 5 rows.", "is_sample": True},
                {"input_data": {"args": [1], "kwargs": {}}, "expected_output": [[1]], "category": "single_row", "difficulty_level": "easy", "explanation": "Single row triangle.", "is_sample": False},
            ],
        },
        128: {
            "function_name": "longestConsecutive",
            "starter_code": "def longestConsecutive(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def longestConsecutive(nums):
                    if not nums:
                        return 0
                    values = set(nums)
                    best = 1
                    for value in values:
                        if value - 1 not in values:
                            current = value
                            while current + 1 in values:
                                current += 1
                            best = max(best, current - value + 1)
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[100, 4, 200, 1, 3, 2]], "kwargs": {}}, "expected_output": 4, "category": "normal", "difficulty_level": "medium", "explanation": "Longest run of consecutive integers.", "is_sample": True},
                {"input_data": {"args": [[0, 3, 7, 2, 5, 8, 4, 6, 0, 1]], "kwargs": {}}, "expected_output": 9, "category": "dense_run", "difficulty_level": "medium", "explanation": "A dense consecutive sequence.", "is_sample": False},
            ],
        },
        133: {
            "function_name": "cloneGraph",
            "starter_code": "def cloneGraph(node):\n    return None",
            "source_code": textwrap.dedent('''
                def cloneGraph(node):
                    if not node:
                        return None
                    visited = {}
                    def dfs(current):
                        if current in visited:
                            return visited[current]
                        clone = {"val": current["val"], "neighbors": []}
                        visited[current] = clone
                        for neighbor in current["neighbors"]:
                            clone["neighbors"].append(dfs(neighbor))
                        return clone
                    return dfs(node)
            ''').strip(),
            "tests": [
                {"input_data": {"args": [{"val": 1, "neighbors": [{"val": 2, "neighbors": []}, {"val": 3, "neighbors": []}]}], "kwargs": {}}, "expected_output": {"val": 1, "neighbors": [{"val": 2, "neighbors": []}, {"val": 3, "neighbors": []}]}, "category": "normal", "difficulty_level": "medium", "explanation": "Graph with two neighbors should be cloned structurally.", "is_sample": True},
            ],
        },
        136: {
            "function_name": "singleNumber",
            "starter_code": "def singleNumber(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def singleNumber(nums):
                    result = 0
                    for value in nums:
                        result ^= value
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 2, 1]], "kwargs": {}}, "expected_output": 1, "category": "normal", "difficulty_level": "easy", "explanation": "Only one value appears once.", "is_sample": True},
                {"input_data": {"args": [[4, 1, 2, 1, 2]], "kwargs": {}}, "expected_output": 4, "category": "distinct", "difficulty_level": "easy", "explanation": "Single odd-occurrence value.", "is_sample": False},
            ],
        },
        138: {
            "function_name": "copyRandomList",
            "starter_code": "def copyRandomList(head):\n    return None",
            "source_code": textwrap.dedent('''
                def copyRandomList(head):
                    if head is None:
                        return None
                    mapping = {}
                    current = head
                    while current is not None:
                        if current not in mapping:
                            mapping[current] = {"val": current["val"], "next": None, "random": None}
                        current = current["next"]
                    current = head
                    while current is not None:
                        copy = mapping[current]
                        copy["next"] = mapping.get(current["next"])
                        copy["random"] = mapping.get(current["random"])
                        current = current["next"]
                    return mapping[head]
            ''').strip(),
            "tests": [
                {"input_data": {"args": [{"val": 7, "next": {"val": 13, "next": {"val": 11, "next": None, "random": None}, "random": {"val": 7, "next": None, "random": None}}, "random": None}], "kwargs": {}}, "expected_output": {"val": 7, "next": {"val": 13, "next": {"val": 11, "next": None, "random": None}, "random": {"val": 7, "next": None, "random": None}}, "random": None}, "category": "normal", "difficulty_level": "medium", "explanation": "A simple linked structure with random pointers.", "is_sample": True},
            ],
        },
        145: {
            "function_name": "postorderTraversal",
            "starter_code": "def postorderTraversal(root):\n    return []",
            "source_code": textwrap.dedent('''
                def postorderTraversal(root):
                    if root is None:
                        return []
                    result = []
                    def visit(node):
                        if node is None:
                            return
                        visit(node[1])
                        visit(node[2])
                        result.append(node[0])
                    visit(root)
                    return result
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, None, [2, [3, None, None], None]]], "kwargs": {}}, "expected_output": [3, 2, 1], "category": "normal", "difficulty_level": "easy", "explanation": "Post-order tree traversal.", "is_sample": True},
                {"input_data": {"args": [[1, None, None]], "kwargs": {}}, "expected_output": [1], "category": "single_node", "difficulty_level": "easy", "explanation": "Single-node tree.", "is_sample": False},
            ],
        },
        147: {
            "function_name": "insertionSortList",
            "starter_code": "def insertionSortList(head):\n    return []",
            "source_code": textwrap.dedent('''
                def insertionSortList(head):
                    nums = head[:]
                    for i in range(1, len(nums)):
                        current = nums[i]
                        j = i - 1
                        while j >= 0 and nums[j] > current:
                            nums[j + 1] = nums[j]
                            j -= 1
                        nums[j + 1] = current
                    return nums
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[4, 2, 1, 3]], "kwargs": {}}, "expected_output": [1, 2, 3, 4], "category": "normal", "difficulty_level": "medium", "explanation": "Sort a list via insertion sort pattern.", "is_sample": True},
                {"input_data": {"args": [[-1, 3, -1, 3]], "kwargs": {}}, "expected_output": [-1, -1, 3, 3], "category": "duplicate_values", "difficulty_level": "easy", "explanation": "Repeated values remain correctly ordered.", "is_sample": False},
            ],
        },
        152: {
            "function_name": "maxProduct",
            "starter_code": "def maxProduct(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def maxProduct(nums):
                    best = current_max = current_min = nums[0]
                    for value in nums[1:]:
                        next_max = max(value, current_max * value, current_min * value)
                        next_min = min(value, current_max * value, current_min * value)
                        current_max, current_min = next_max, next_min
                        best = max(best, current_max)
                    return best
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[2, 3, -2, 4]], "kwargs": {}}, "expected_output": 6, "category": "normal", "difficulty_level": "medium", "explanation": "Maximum product of a contiguous subarray.", "is_sample": True},
                {"input_data": {"args": [[-2, 0, -1]], "kwargs": {}}, "expected_output": 0, "category": "zero_prefix", "difficulty_level": "easy", "explanation": "Zero can dominate the product for a segment.", "is_sample": False},
            ],
        },
        154: {
            "function_name": "findMin",
            "starter_code": "def findMin(nums):\n    return 0",
            "source_code": textwrap.dedent('''
                def findMin(nums):
                    left, right = 0, len(nums) - 1
                    while left < right:
                        mid = (left + right) // 2
                        if nums[mid] > nums[right]:
                            left = mid + 1
                        else:
                            right = mid
                    return nums[left]
            ''').strip(),
            "tests": [
                {"input_data": {"args": [[1, 3, 5]], "kwargs": {}}, "expected_output": 1, "category": "normal", "difficulty_level": "medium", "explanation": "Sorted array already in rotation order.", "is_sample": True},
                {"input_data": {"args": [[2, 2, 2, 0, 1]], "kwargs": {}}, "expected_output": 0, "category": "duplicate_values", "difficulty_level": "hard", "explanation": "Repeated minima values still reduce to the rotation point.", "is_sample": False},
            ],
        },
        157: {
            "function_name": "readNCharacters",
            "starter_code": "def readNCharacters(data, n):\n    return ''",
            "source_code": textwrap.dedent('''
                def readNCharacters(data, n):
                    return data[:n]
            ''').strip(),
            "tests": [
                {"input_data": {"args": ["abcdef", 4], "kwargs": {}}, "expected_output": "abcd", "category": "normal", "difficulty_level": "easy", "explanation": "Read up to N characters from a string buffer.", "is_sample": True},
                {"input_data": {"args": ["abc", 10], "kwargs": {}}, "expected_output": "abc", "category": "overflow", "difficulty_level": "easy", "explanation": "Requested size exceeds available input.", "is_sample": False},
            ],
        },
    }

    total = 0
    playlist_ids = google_playlist_problem_ids()
    for problem_id in playlist_ids:
        fixture = problem_specs.get(problem_id)
        if fixture is None:
            continue
        total += ensure_problem_support(problem_id, fixture["function_name"], fixture["starter_code"], fixture["source_code"], fixture["tests"])
    return total


if __name__ == "__main__":
    seeded = seed_google_problem_support()
    print(f"Seeded {seeded} Google CodeTutor-authored problem cases.")
