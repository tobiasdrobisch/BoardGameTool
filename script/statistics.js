// ======================= STATISTICS.JS =======================

// DOM Elements
const statsViewSelect = document.getElementById("statsView");
const comparePlayersSelect = document.getElementById("comparePlayers");

// global allMatches comes from main HTML script
// let allMatches = [];

// ----------------------- UI HELPERS -----------------------

function populateComparePlayers(matches) {
  if (!comparePlayersSelect) return;

  const playerSet = new Set();

  matches.forEach(m => {
    if (!m.scores) return;

    Object.values(m.scores).forEach(s => {
      if (s.username) playerSet.add(s.username);
    });
  });

  const players = Array.from(playerSet).sort();

  comparePlayersSelect.innerHTML = players
    .map(p => `<option value="${p}">${p}</option>`)
    .join("");

  // Auto-select first two if available
  if (players.length > 0) comparePlayersSelect.options[0].selected = true;
  if (players.length > 1) comparePlayersSelect.options[1].selected = true;
}

function getSelectedComparePlayers() {
  if (!comparePlayersSelect) return [];
  return Array.from(comparePlayersSelect.selectedOptions).map(o => o.value);
}

// ----------------------- DATA BUILDERS -----------------------

// Total score across all matches
function buildPlayerTotalScores(matches, selectedPlayers = []) {
  const totals = {};

  matches.forEach(match => {
    if (!match.scores) return;

    Object.values(match.scores).forEach(playerScore => {
      const username = playerScore.username;
      if (!username) return;

      if (selectedPlayers.length && !selectedPlayers.includes(username)) return;

      const score = playerScore.score || 0;
      if (!totals[username]) totals[username] = 0;
      totals[username] += score;
    });
  });

  return Object.entries(totals).map(([player, score]) => ({
    player,
    score
  }));
}

// Wins count
function buildPlayerWins(matches, selectedPlayers = []) {
  const wins = {};

  matches.forEach(match => {
    if (!match.scores) return;

    const scoresArray = Object.values(match.scores);
    if (!scoresArray.length) return;

    const maxScore = Math.max(...scoresArray.map(s => s.score || 0));
    const winners = scoresArray.filter(s => (s.score || 0) === maxScore);

    winners.forEach(w => {
      const username = w.username;
      if (!username) return;

      if (selectedPlayers.length && !selectedPlayers.includes(username)) return;

      if (!wins[username]) wins[username] = 0;
      wins[username] += 1;
    });
  });

  return Object.entries(wins).map(([player, score]) => ({
    player,
    score
  }));
}

// Tasks played count
function buildTasksPlayed(matches) {
  const taskCounts = {};

  matches.forEach(match => {
    if (!match.tasks) return;

    match.tasks.forEach(task => {
      if (!task?.name) return;

      const taskName = task.name;
      if (!taskCounts[taskName]) taskCounts[taskName] = 0;
      taskCounts[taskName] += 1;
    });
  });

  return Object.entries(taskCounts).map(([task, count]) => ({
    task,
    count
  }));
}

// Score progress (line chart)
function buildScoreProgress(matches, selectedPlayers) {

  // sort by created_at
  const sorted = [...matches].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

  const progress = selectedPlayers.map(player => ({
    player,
    values: []
  }));

  sorted.forEach((match, index) => {

    selectedPlayers.forEach(player => {
      let score = 0;

      if (match.scores) {
        const found = Object.values(match.scores).find(s => s.username === player);
        score = found ? (found.score || 0) : 0;
      }

      const obj = progress.find(p => p.player === player);
      obj.values.push({
        game: index + 1,
        score
      });
    });
  });

  return progress;
}

// ----------------------- CHARTS -----------------------

function renderBarChart(data, labelKey, valueKey, titleText) {
  d3.select("#visualisation").html("");

  if (!data || !data.length) {
    d3.select("#visualisation").text("No data available");
    return;
  }

  const width = 900;
  const height = 450;
  const margin = { top: 40, right: 20, bottom: 140, left: 60 };

  data.sort((a, b) => b[valueKey] - a[valueKey]);

  const svg = d3.select("#visualisation")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const x = d3.scaleBand()
    .domain(data.map(d => d[labelKey]))
    .range([margin.left, width - margin.right])
    .padding(0.2);

  const y = d3.scaleLinear()
    .domain([0, d3.max(data, d => d[valueKey])])
    .nice()
    .range([height - margin.bottom, margin.top]);

  // Bars
  svg.append("g")
    .selectAll("rect")
    .data(data)
    .enter()
    .append("rect")
    .attr("x", d => x(d[labelKey]))
    .attr("y", d => y(d[valueKey]))
    .attr("width", x.bandwidth())
    .attr("height", d => y(0) - y(d[valueKey]))
    .attr("fill", "steelblue");

  // X Axis
  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x))
    .selectAll("text")
    .attr("transform", "rotate(-35)")
    .style("text-anchor", "end");

  // Y Axis
  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y));

  // Title
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", 25)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .style("font-weight", "bold")
    .text(titleText);
}

function renderLineChart(progressData) {
  d3.select("#visualisation").html("");

  if (!progressData || !progressData.length) {
    d3.select("#visualisation").text("No data available");
    return;
  }

  const width = 900;
  const height = 450;
  const margin = { top: 40, right: 200, bottom: 60, left: 60 };

  const svg = d3.select("#visualisation")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  const allValues = progressData.flatMap(p => p.values);

  const x = d3.scaleLinear()
    .domain([1, d3.max(allValues, d => d.game)])
    .range([margin.left, width - margin.right]);

  const y = d3.scaleLinear()
    .domain([0, d3.max(allValues, d => d.score)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const line = d3.line()
    .x(d => x(d.game))
    .y(d => y(d.score));

  // first blue, second red
  const colors = ["steelblue", "red", "green", "orange", "purple"];

  progressData.forEach((playerData, idx) => {

    svg.append("path")
      .datum(playerData.values)
      .attr("fill", "none")
      .attr("stroke", colors[idx % colors.length])
      .attr("stroke-width", 3)
      .attr("d", line);

    // Points
    svg.append("g")
      .selectAll("circle")
      .data(playerData.values)
      .enter()
      .append("circle")
      .attr("cx", d => x(d.game))
      .attr("cy", d => y(d.score))
      .attr("r", 4)
      .attr("fill", colors[idx % colors.length]);

    // Legend
    svg.append("text")
      .attr("x", width - margin.right + 20)
      .attr("y", margin.top + idx * 22)
      .attr("fill", colors[idx % colors.length])
      .style("font-size", "14px")
      .style("font-weight", "bold")
      .text(playerData.player);
  });

  // Axes
  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(10).tickFormat(d3.format("d")));

  svg.append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y));

  // Title
  svg.append("text")
    .attr("x", width / 2)
    .attr("y", 25)
    .attr("text-anchor", "middle")
    .style("font-size", "16px")
    .style("font-weight", "bold")
    .text("Score Progress per Match");
}

// ----------------------- MAIN UPDATE -----------------------

function updateStatisticsView() {
  if (!statsViewSelect) return;

  const view = statsViewSelect.value;
  const selectedPlayers = getSelectedComparePlayers();

  if (view === "totalScores") {
    const data = buildPlayerTotalScores(allMatches, selectedPlayers);
    renderBarChart(data, "player", "score", "Total Scores (Selected Players)");
  }

  if (view === "wins") {
    const data = buildPlayerWins(allMatches, selectedPlayers);
    renderBarChart(data, "player", "score", "Wins (Selected Players)");
  }

  if (view === "tasksPlayed") {
    const data = buildTasksPlayed(allMatches);
    renderBarChart(data, "task", "count", "Tasks played (All Matches)");
  }

  if (view === "scoreProgress") {
    if (!selectedPlayers.length) {
      d3.select("#visualisation").html("Select at least one player.");
      return;
    }

    const progressData = buildScoreProgress(allMatches, selectedPlayers);
    renderLineChart(progressData);
  }
}

// ----------------------- EVENTS -----------------------

if (statsViewSelect) {
  statsViewSelect.addEventListener("change", updateStatisticsView);
}

if (comparePlayersSelect) {
  comparePlayersSelect.addEventListener("change", updateStatisticsView);
}