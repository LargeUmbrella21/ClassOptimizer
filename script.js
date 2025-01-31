// Sample class list, similar to the Tkinter use case
const classList = [
  "Calculus I",
  "Physics II",
  "Data Structures",
  "Organic Chemistry",
  "Linear Algebra",
  "AI in Robotics",
  "Game Development"
];

const dropdown = document.getElementById("available-classes");
const rankingList = document.getElementById("ranked-classes");
const generateButton = document.getElementById("generate-rankings");

// Populate dropdown menu
function populateDropdown() {
  classList.forEach(course => {
    const option = document.createElement("option");
    option.value = course;
    option.textContent = course;
    dropdown.appendChild(option);
  });
}

// Generate top 5 random rankings
function generateTopRankings() {
  // Clear existing list
  rankingList.innerHTML = "";

  // Shuffle courses and pick the top 5
  const shuffledClasses = [...classList].sort(() => 0.5 - Math.random());
  const top5Classes = shuffledClasses.slice(0, 5);

  top5Classes.forEach(course => {
    const li = document.createElement("li");
    li.textContent = course;
    rankingList.appendChild(li);
  });
}

generateButton.addEventListener("click", generateTopRankings);

// Initialize dropdown on page load
window.onload = populateDropdown;
