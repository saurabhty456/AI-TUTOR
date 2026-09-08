// Central place for quiz types, mock question data, and helper functions.
// Swapping this for a real backend later should not require touching any
// component's rendering logic — only these functions.

export type Difficulty = "Easy" | "Medium" | "Hard";

export interface QuizQuestionData {
  id: string;
  question: string;
  codeSnippet?: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  difficulty: Difficulty;
}

export interface Topic {
  id: string;
  name: string;
  description: string;
  icon: string;
  questions: QuizQuestionData[];
}

export type QuestionCount = 5 | 10 | 15;
export type TimerMinutes = 0 | 10 | 15 | 20; // 0 = no timer

export interface QuizConfig {
  difficulty: Difficulty;
  questionCount: QuestionCount;
  timerMinutes: TimerMinutes;
}

export interface QuizResult {
  topicId: string;
  topicName: string;
  difficulty: Difficulty;
  timerMinutes: TimerMinutes;
  questions: QuizQuestionData[];
  userAnswers: (number | null)[];
  score: number;
  total: number;
  percentage: number;
  unanswered: number;
  timeTakenSeconds: number;
  completedAt: string;
}

export interface QuizHistoryEntry {
  id: number;
  topic: string;
  difficulty: string;
  total_questions: number;
  correct_answers: number;
  wrong_answers: number;
  unanswered_questions: number;
  score_percentage: number;
  time_limit: number;
  completed_at: string;
}

export function formatQuizDate(value: string): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export function formatQuizTime(value: string): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

// ---------------------------------------------------------------------
// Mock question bank — at least 6 realistic, technically accurate
// questions per topic, tagged by difficulty. Not connected to any
// backend yet.
// ---------------------------------------------------------------------

export const TOPICS: Topic[] = [
  {
    id: "python",
    name: "Python",
    description: "Core syntax, data types, functions, and OOP basics.",
    icon: "🐍",
    questions: [
      {
        id: "py-1",
        question: "Which of the following is a mutable data type in Python?",
        options: ["Tuple", "String", "List", "Integer"],
        correctIndex: 2,
        explanation:
          "Lists are mutable, meaning their contents can be changed after creation, unlike tuples, strings, and integers, which are immutable.",
        difficulty: "Easy",
      },
      {
        id: "py-2",
        question: "What does the following code print?",
        codeSnippet: "print(type([]))",
        options: [
          "<class 'list'>",
          "<class 'dict'>",
          "<class 'tuple'>",
          "<class 'set'>",
        ],
        correctIndex: 0,
        explanation:
          "[] creates an empty list, so type() returns <class 'list'>.",
        difficulty: "Easy",
      },
      {
        id: "py-3",
        question:
          "What will my_dict.get('x', 0) return if 'x' is not a key in my_dict?",
        options: ["None", "KeyError", "0", "False"],
        correctIndex: 2,
        explanation:
          "The second argument to dict.get() is the default value returned when the key is missing, so it returns 0.",
        difficulty: "Medium",
      },
      {
        id: "py-4",
        question: "What is the output of print(3 == 3.0)?",
        options: ["True", "False", "Error", "None"],
        correctIndex: 0,
        explanation:
          "Python compares numeric values, not types, so an int and a float with equal value are considered equal.",
        difficulty: "Medium",
      },
      {
        id: "py-5",
        question: "Which keyword is used to handle exceptions in Python?",
        options: ["catch", "except", "rescue", "handle"],
        correctIndex: 1,
        explanation:
          "Python uses try/except blocks to catch and handle exceptions.",
        difficulty: "Hard",
      },
      {
        id: "py-6",
        question: "What does the self parameter refer to in a class method?",
        options: [
          "The class itself",
          "The parent class",
          "The current instance",
          "A static variable",
        ],
        correctIndex: 2,
        explanation:
          "self refers to the specific instance the method is being called on, giving access to its attributes.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "javascript",
    name: "JavaScript",
    description: "Variables, closures, arrays, and asynchronous code.",
    icon: "🟨",
    questions: [
      {
        id: "js-1",
        question:
          "Which keyword declares a block-scoped variable in JavaScript?",
        options: ["var", "let", "function", "global"],
        correctIndex: 1,
        explanation:
          "let (and const) are block-scoped, while var is function-scoped.",
        difficulty: "Easy",
      },
      {
        id: "js-2",
        question: "What does typeof [] return in JavaScript?",
        options: ["'array'", "'object'", "'list'", "'undefined'"],
        correctIndex: 1,
        explanation:
          "Arrays are technically objects in JavaScript, so typeof returns 'object'.",
        difficulty: "Easy",
      },
      {
        id: "js-3",
        question: "What is a closure in JavaScript?",
        options: [
          "A loop that never ends",
          "A function bundled with its lexical scope",
          "A type of array",
          "A CSS property",
        ],
        correctIndex: 1,
        explanation:
          "A closure is a function that retains access to variables from its enclosing scope even after that scope has finished executing.",
        difficulty: "Medium",
      },
      {
        id: "js-4",
        question: "What does Array.prototype.map() return?",
        options: [
          "The original array modified",
          "A new array with transformed elements",
          "A single value",
          "undefined",
        ],
        correctIndex: 1,
        explanation:
          "map() creates a new array by applying a function to every element, leaving the original array unchanged.",
        difficulty: "Medium",
      },
      {
        id: "js-5",
        question: "What does a Promise represent in JavaScript?",
        options: [
          "A synchronous function call",
          "A value that may be available now, later, or never",
          "A type of loop",
          "A CSS animation",
        ],
        correctIndex: 1,
        explanation:
          "A Promise represents the eventual completion (or failure) of an asynchronous operation.",
        difficulty: "Hard",
      },
      {
        id: "js-6",
        question:
          "Which keyword pauses execution of an async function until a Promise resolves?",
        options: ["wait", "await", "pause", "hold"],
        correctIndex: 1,
        explanation:
          "await pauses execution inside an async function until the awaited Promise settles.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "data-structures",
    name: "Data Structures",
    description: "Stacks, queues, linked lists, trees, and hash tables.",
    icon: "🗂️",
    questions: [
      {
        id: "ds-1",
        question:
          "Which data structure uses LIFO (Last In, First Out) ordering?",
        options: ["Queue", "Stack", "Linked List", "Tree"],
        correctIndex: 1,
        explanation:
          "A stack adds and removes elements from the same end, making the last item added the first one removed.",
        difficulty: "Easy",
      },
      {
        id: "ds-2",
        question:
          "Which data structure uses FIFO (First In, First Out) ordering?",
        options: ["Stack", "Queue", "Graph", "Heap"],
        correctIndex: 1,
        explanation:
          "A queue removes elements in the same order they were added.",
        difficulty: "Easy",
      },
      {
        id: "ds-3",
        question: "What is the main advantage of a linked list over an array?",
        options: [
          "Faster indexing",
          "Efficient insertion/deletion without shifting elements",
          "Uses less memory always",
          "Better cache performance",
        ],
        correctIndex: 1,
        explanation:
          "Linked lists allow O(1) insertion/deletion at a known position without shifting other elements, unlike arrays.",
        difficulty: "Medium",
      },
      {
        id: "ds-4",
        question:
          "What is the average time complexity of a hash table lookup?",
        options: ["O(n)", "O(log n)", "O(1)", "O(n²)"],
        correctIndex: 2,
        explanation:
          "With a good hash function, hash table lookups average O(1) time.",
        difficulty: "Medium",
      },
      {
        id: "ds-5",
        question:
          "In a binary search tree, where are values smaller than the root stored?",
        options: ["Right subtree", "Left subtree", "Root itself", "Randomly"],
        correctIndex: 1,
        explanation:
          "By BST property, all values smaller than a node are placed in its left subtree.",
        difficulty: "Hard",
      },
      {
        id: "ds-6",
        question:
          "What is the worst-case time complexity of searching an unbalanced binary search tree?",
        options: ["O(log n)", "O(1)", "O(n)", "O(n log n)"],
        correctIndex: 2,
        explanation:
          "If the tree becomes skewed like a linked list, search degrades to O(n).",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "algorithms",
    name: "Algorithms",
    description: "Searching, sorting, Big-O, and graph traversal.",
    icon: "🧮",
    questions: [
      {
        id: "algo-1",
        question:
          "What is the time complexity of binary search on a sorted array?",
        options: ["O(n)", "O(log n)", "O(n²)", "O(1)"],
        correctIndex: 1,
        explanation:
          "Binary search halves the search space each step, giving logarithmic time complexity.",
        difficulty: "Easy",
      },
      {
        id: "algo-2",
        question:
          "Which sorting algorithm repeatedly swaps adjacent elements if they are in the wrong order?",
        options: ["Bubble Sort", "Merge Sort", "Quick Sort", "Heap Sort"],
        correctIndex: 0,
        explanation:
          "Bubble sort compares and swaps adjacent elements, 'bubbling' the largest values toward the end.",
        difficulty: "Easy",
      },
      {
        id: "algo-3",
        question: "What is the worst-case time complexity of Quicksort?",
        options: ["O(n log n)", "O(n)", "O(n²)", "O(log n)"],
        correctIndex: 2,
        explanation:
          "Quicksort degrades to O(n²) when pivot choices consistently create unbalanced partitions.",
        difficulty: "Medium",
      },
      {
        id: "algo-4",
        question: "Which data structure does BFS (Breadth-First Search) use?",
        options: ["Stack", "Queue", "Recursion only", "Priority queue only"],
        correctIndex: 1,
        explanation:
          "BFS uses a queue to explore nodes level by level.",
        difficulty: "Medium",
      },
      {
        id: "algo-5",
        question:
          "Which algorithm is guaranteed to find the shortest path in a weighted graph with non-negative weights?",
        options: ["DFS", "BFS", "Dijkstra's Algorithm", "Bubble Sort"],
        correctIndex: 2,
        explanation:
          "Dijkstra's algorithm finds shortest paths in graphs with non-negative edge weights.",
        difficulty: "Hard",
      },
      {
        id: "algo-6",
        question:
          "What does DFS (Depth-First Search) use to keep track of nodes to visit?",
        options: ["Queue", "Stack (or recursion)", "Hash table", "Heap"],
        correctIndex: 1,
        explanation:
          "DFS explores as far as possible along each branch using a stack or the recursive call stack before backtracking.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "oop",
    name: "OOP",
    description: "Encapsulation, inheritance, polymorphism, and abstraction.",
    icon: "🧩",
    questions: [
      {
        id: "oop-1",
        question: "What is encapsulation in OOP?",
        options: [
          "Hiding internal state and requiring interaction through methods",
          "Creating multiple classes",
          "Copying code",
          "Running code faster",
        ],
        correctIndex: 0,
        explanation:
          "Encapsulation bundles data and methods together while restricting direct access to internal state.",
        difficulty: "Easy",
      },
      {
        id: "oop-2",
        question: "What is inheritance in OOP?",
        options: [
          "A class copying another class's file",
          "A class acquiring properties/methods from another class",
          "Deleting unused code",
          "A type of loop",
        ],
        correctIndex: 1,
        explanation:
          "Inheritance lets a class reuse and extend behavior from a parent class.",
        difficulty: "Easy",
      },
      {
        id: "oop-3",
        question: "What is polymorphism in OOP?",
        options: [
          "Objects taking many forms via a common interface",
          "Having many classes with the same name",
          "Using multiple databases",
          "Compiling code multiple times",
        ],
        correctIndex: 0,
        explanation:
          "Polymorphism lets objects of different classes be treated through a shared interface, each implementing behavior differently.",
        difficulty: "Medium",
      },
      {
        id: "oop-4",
        question: "What is an abstract class typically used for?",
        options: [
          "Storing data only",
          "Defining a template that other classes must implement",
          "Running unit tests",
          "Formatting output",
        ],
        correctIndex: 1,
        explanation:
          "Abstract classes define a common structure/interface, leaving specific implementation to subclasses.",
        difficulty: "Medium",
      },
      {
        id: "oop-5",
        question: "What does 'method overriding' mean?",
        options: [
          "Defining multiple methods with the same name but different parameters",
          "A subclass providing its own implementation of a method from its parent",
          "Deleting a method",
          "Renaming a variable",
        ],
        correctIndex: 1,
        explanation:
          "Method overriding lets a subclass redefine a parent class method's behavior.",
        difficulty: "Hard",
      },
      {
        id: "oop-6",
        question: "What is a key benefit of abstraction in OOP?",
        options: [
          "It exposes all implementation details",
          "It reduces complexity by hiding unnecessary details",
          "It slows down development",
          "It removes the need for classes",
        ],
        correctIndex: 1,
        explanation:
          "Abstraction focuses on essential features while hiding implementation complexity from the user.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "sql",
    name: "SQL",
    description: "Queries, joins, grouping, and aggregation.",
    icon: "🗄️",
    questions: [
      {
        id: "sql-1",
        question:
          "Which SQL keyword is used to retrieve data from a database?",
        options: ["GET", "SELECT", "FETCH", "FIND"],
        correctIndex: 1,
        explanation:
          "SELECT is the standard SQL command for querying data from tables.",
        difficulty: "Easy",
      },
      {
        id: "sql-2",
        question: "Which clause filters rows before grouping?",
        options: ["HAVING", "WHERE", "GROUP BY", "ORDER BY"],
        correctIndex: 1,
        explanation:
          "WHERE filters individual rows before any grouping occurs; HAVING filters after grouping.",
        difficulty: "Easy",
      },
      {
        id: "sql-3",
        question: "Which JOIN returns only matching rows from both tables?",
        options: ["LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "FULL OUTER JOIN"],
        correctIndex: 2,
        explanation:
          "INNER JOIN returns only rows that have matching values in both joined tables.",
        difficulty: "Medium",
      },
      {
        id: "sql-4",
        question: "What does GROUP BY do?",
        options: [
          "Sorts rows alphabetically",
          "Groups rows sharing a value so aggregate functions can be applied",
          "Deletes duplicate rows",
          "Joins two tables",
        ],
        correctIndex: 1,
        explanation:
          "GROUP BY groups rows with the same values so functions like COUNT or SUM can summarize each group.",
        difficulty: "Medium",
      },
      {
        id: "sql-5",
        question: "Which clause is used to filter groups after a GROUP BY?",
        options: ["WHERE", "HAVING", "FILTER", "LIMIT"],
        correctIndex: 1,
        explanation:
          "HAVING filters aggregated groups, whereas WHERE filters rows before aggregation.",
        difficulty: "Hard",
      },
      {
        id: "sql-6",
        question: "What does the aggregate function COUNT(*) do?",
        options: [
          "Counts distinct values only",
          "Counts all rows, including NULLs",
          "Sums all numeric columns",
          "Returns the largest value",
        ],
        correctIndex: 1,
        explanation:
          "COUNT(*) counts every row in the result set, regardless of NULL values in any particular column.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "html-css",
    name: "HTML & CSS",
    description: "Semantic markup, Flexbox, Grid, and responsive design.",
    icon: "🎨",
    questions: [
      {
        id: "hc-1",
        question:
          "Which HTML tag is used to define the main navigation links of a page?",
        options: ["<div>", "<nav>", "<section>", "<header>"],
        correctIndex: 1,
        explanation:
          "<nav> is the semantic element intended for major navigation blocks.",
        difficulty: "Easy",
      },
      {
        id: "hc-2",
        question: "Which CSS property is used to change text color?",
        options: ["font-color", "text-color", "color", "background-color"],
        correctIndex: 2,
        explanation: "The color property sets the color of text content.",
        difficulty: "Easy",
      },
      {
        id: "hc-3",
        question:
          "In Flexbox, which property aligns items along the main axis?",
        options: [
          "align-items",
          "justify-content",
          "flex-direction",
          "align-self",
        ],
        correctIndex: 1,
        explanation:
          "justify-content controls alignment along the main axis, while align-items controls the cross axis.",
        difficulty: "Medium",
      },
      {
        id: "hc-4",
        question:
          "Which CSS Grid property defines the number and size of columns?",
        options: [
          "grid-template-columns",
          "grid-gap",
          "grid-area",
          "grid-auto-flow",
        ],
        correctIndex: 0,
        explanation:
          "grid-template-columns explicitly defines the column structure of a grid container.",
        difficulty: "Medium",
      },
      {
        id: "hc-5",
        question:
          "Which selector has higher specificity: a class or an ID?",
        options: ["Class", "ID", "They are equal", "Neither has specificity"],
        correctIndex: 1,
        explanation:
          "ID selectors have higher specificity than class selectors in CSS's specificity hierarchy.",
        difficulty: "Hard",
      },
      {
        id: "hc-6",
        question: "Which meta tag is essential for responsive design?",
        options: [
          "<meta charset>",
          "<meta name='viewport'>",
          "<meta name='description'>",
          "<meta http-equiv='refresh'>",
        ],
        correctIndex: 1,
        explanation:
          "The viewport meta tag controls how a page scales and behaves on different screen sizes.",
        difficulty: "Hard",
      },
    ],
  },
  {
    id: "cs-basics",
    name: "Computer Science Basics",
    description: "Operating systems, networking, databases, and memory.",
    icon: "🖥️",
    questions: [
      {
        id: "cs-1",
        question: "What is the primary role of an operating system?",
        options: [
          "Compile source code",
          "Manage hardware resources and provide services to programs",
          "Design web pages",
          "Write documentation",
        ],
        correctIndex: 1,
        explanation:
          "An OS manages hardware (CPU, memory, devices) and provides a platform for running applications.",
        difficulty: "Easy",
      },
      {
        id: "cs-2",
        question: "What does RAM stand for?",
        options: [
          "Read Access Memory",
          "Random Access Memory",
          "Rapid Application Memory",
          "Runtime Allocation Module",
        ],
        correctIndex: 1,
        explanation:
          "RAM stands for Random Access Memory, used for fast, temporary data storage while a program runs.",
        difficulty: "Easy",
      },
      {
        id: "cs-3",
        question: "What is the purpose of a process in an operating system?",
        options: [
          "A stored file on disk",
          "An instance of a running program",
          "A type of network packet",
          "A hardware component",
        ],
        correctIndex: 1,
        explanation:
          "A process represents a program that is currently being executed, with its own memory and resources.",
        difficulty: "Medium",
      },
      {
        id: "cs-4",
        question: "What does DNS do in computer networking?",
        options: [
          "Encrypts network traffic",
          "Translates domain names into IP addresses",
          "Compresses files for transfer",
          "Manages CPU scheduling",
        ],
        correctIndex: 1,
        explanation:
          "DNS (Domain Name System) resolves human-readable domain names into the IP addresses computers use to communicate.",
        difficulty: "Medium",
      },
      {
        id: "cs-5",
        question: "What is a deadlock in operating systems?",
        options: [
          "A fast processing state",
          "A situation where processes wait forever for resources held by each other",
          "A type of memory leak",
          "A network timeout",
        ],
        correctIndex: 1,
        explanation:
          "A deadlock occurs when two or more processes each wait for a resource the other holds, so none can proceed.",
        difficulty: "Hard",
      },
      {
        id: "cs-6",
        question: "What is the main purpose of database indexing?",
        options: [
          "To encrypt data",
          "To speed up data retrieval",
          "To reduce storage size only",
          "To back up data automatically",
        ],
        correctIndex: 1,
        explanation:
          "Indexes create data structures that make searching and retrieving specific rows much faster.",
        difficulty: "Hard",
      },
    ],
  },
];

export function getTopicById(id: string): Topic | undefined {
  return TOPICS.find((t) => t.id === id);
}

function shuffle<T>(items: T[]): T[] {
  const copy = [...items];
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy;
}

/**
 * Builds a quiz question list for a topic/difficulty/count.
 * The mock bank only has 6 questions per topic, so when more are
 * requested (10 or 15) the shuffled pool repeats to fill the count.
 * Replace this with a real API call later — callers only depend on
 * getting back a QuizQuestionData[] of the requested length.
 */
export function generateQuizQuestions(
  topic: Topic,
  difficulty: Difficulty,
  count: number
): QuizQuestionData[] {
  const matching = topic.questions.filter((q) => q.difficulty === difficulty);
  const pool = shuffle(matching.length > 0 ? matching : topic.questions);

  const result: QuizQuestionData[] = [];
  for (let i = 0; i < count; i++) {
    result.push(pool[i % pool.length]);
  }
  return result;
}

export function formatTime(totalSeconds: number): string {
  const safe = Math.max(0, totalSeconds);
  const minutes = Math.floor(safe / 60);
  const seconds = safe % 60;
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(
    2,
    "0"
  )}`;
}

export function getPerformanceMessage(percentage: number): string {
  if (percentage >= 90) {
    return "Excellent! You have a strong understanding of this topic.";
  }
  if (percentage >= 70) {
    return "Great work! A little more practice will make you even stronger.";
  }
  if (percentage >= 50) {
    return "Good start! Review the missed concepts and try again.";
  }
  return "Keep practicing — review the explanations below and try again.";
}
