// simpleUploadFilter.js

let filteredPredicates = predicates; // default to all predicates

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('upload-datapackage');
  if (!input) {
    console.error("❌ Upload input not found in DOM");
    return;
  }

  console.log("✅ Upload handler bound to input");

  input.addEventListener('change', function (e) {
    const file = e.target.files[0];
    console.log("File selected:", file);
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (event) {
      try {
        const json = JSON.parse(event.target.result);
        console.log("File loaded, JSON parsed:", json);

        if (!Array.isArray(json.resources)) {
          alert("Invalid datapackage.json: missing 'resources'");
          return;
        }

        // Extract table names from datapackage.json
        const tableNames = new Set(json.resources.map(r => r.name));

        // Filter indexJson.tableSchemas in-place
        indexJson.tableSchemas = indexJson.tableSchemas.filter(t => tableNames.has(t.name));

        const presentTableNames = new Set(indexJson.tableSchemas.map(t => t.name));

        // Filter predicates without modifying the global constant
        filteredPredicates = predicates.filter(p =>
          tableNames.has(p.subject_table) && tableNames.has(p.related_table)
        );

        // Rebuild and re-render graph
        focal = indexJson.tableSchemas[0]?.name || "event";
        fullData = buildGraphData();
        renderGraph();

        document.querySelectorAll('.table-link').forEach(link => {
          const tableName = link.getAttribute('data-target');
          const isPresent = presentTableNames.has(tableName);
          link.style.color = isPresent ? '#0645AD' : '#999';
          link.style.pointerEvents = isPresent ? 'auto' : 'none';
        });

        // Disable category checkboxes if no matching tables are present
        const presentCategories = new Set();
        indexJson.tableSchemas.forEach(t => {
          const name = t.name.toLowerCase();
          if (name.includes('agent')) presentCategories.add('agent');
          if (name.includes('assertion')) presentCategories.add('assertion');
          if (name.includes('identifier')) presentCategories.add('identifier');
          if (name.includes('media')) presentCategories.add('media');
          if (name.includes('protocol')) presentCategories.add('protocol');
          if (name.includes('reference')) presentCategories.add('reference');
        });

        document.querySelectorAll('.category-filter').forEach(input => {
          const category = input.value.toLowerCase();
          const enabled = presentCategories.has(category);
          input.disabled = !enabled;
          input.parentElement.style.color = enabled ? 'inherit' : '#999';
        });


      } catch (err) {
        console.error("Failed to parse datapackage.json:", err.message, err.stack);
        alert("Could not parse datapackage.json file. See console for details.");
      }
    };

    reader.readAsText(file);
  });
});

// Define buildGraphData locally for use in upload flow
function buildGraphData() {
  const nodes = indexJson.tableSchemas.map(schema => ({
    data: { id: schema.name }
  }));

  const edges = filteredPredicates.map((pred, index) => ({
    data: {
      id: `${pred.subject_table}_${pred.subject_field}_${pred.related_table}_${pred.related_field}_${index}`,
      source: pred.subject_table,
      target: pred.related_table,
      label: pred.predicate,
      source_field: `${pred.subject_table}.${pred.subject_field}`,
      target_field: `${pred.related_table}.${pred.related_field}`
    }
  }));

  return { nodes, edges };
}
