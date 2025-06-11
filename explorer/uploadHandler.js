// uploadHandler.js

function initializeUploadHandler(indexJsonRef, predicatesRef, onSuccess) {
  const input = document.getElementById('upload-datapackage');
  if (!input) return;

  input.addEventListener('change', function (e) {
    const file = e.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = function (event) {
      try {
        const json = JSON.parse(event.target.result);
        if (!json.resources || !Array.isArray(json.resources)) {
          throw new Error("Missing or invalid 'resources' in datapackage.json");
        }

        // Overwrite indexJson
        indexJsonRef.tableSchemas = json.resources.map(r => {
          const schema = r.schema || {};
          return {
            name: r.name,
            title: schema.title || r.name,
            description: schema.description || '',
            comments: '',
            examples: '',
            url: schema.url || '',
            fields: schema.fields || []
          };
        });

        // Overwrite predicates
        predicatesRef.length = 0;
        json.resources.forEach(r => {
          const source = r.name;
          const schema = r.schema || {};
          (schema.foreignKeys || []).forEach(fk => {
            const fields = Array.isArray(fk.fields) ? fk.fields : [fk.fields];
            const refs = Array.isArray(fk.reference.fields) ? fk.reference.fields : [fk.reference.fields];
            const target = fk.reference.resource;
            for (let i = 0; i < fields.length; i++) {
              predicatesRef.push({
                subject_table: source,
                subject_field: fields[i],
                related_table: target,
                related_field: refs[i],
                predicate: `${fields[i]} → ${refs[i]}`
              });
            }
          });
        });

        // Trigger re-render with the new focal
        const firstTable = json.resources[0]?.name || 'event';
        onSuccess(firstTable);

      } catch (err) {
        console.error('Error parsing uploaded file:', err);
        alert("Invalid datapackage.json file.");
      }
    };

    reader.readAsText(file);
  });
}
