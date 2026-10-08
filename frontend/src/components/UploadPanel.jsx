import { useRef } from "react";


function UploadPanel({
  onUpload,
  loading,
}) {
  const fileInputRef =
    useRef(null);


  function handleFileChange(event) {
    const file =
      event.target.files?.[0];

    if (!file) {
      return;
    }

    onUpload(file);

    event.target.value = "";
  }


  function handleDemo() {
    const demoFile =
      new File(
        ["AMLens demo transaction dataset"],
        "demo.csv",
        {
          type: "text/csv",
        }
      );

    onUpload(demoFile);
  }


  return (
    <section className="upload-panel">

      <div className="upload-copy">

        <div className="upload-icon">
          ⇧
        </div>

        <div>

          <h3>
            Transaction Analysis
          </h3>

          <p>
            Upload transaction data or load the
            AMLens demonstration dataset.
          </p>

        </div>

      </div>


      <div className="upload-actions">

        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,text/csv"
          hidden
          onChange={handleFileChange}
        />


        <button
          className="secondary-button"
          onClick={() =>
            fileInputRef.current?.click()
          }
          disabled={loading}
        >
          Upload CSV
        </button>


        <button
          className="primary-button"
          onClick={handleDemo}
          disabled={loading}
        >
          {loading
            ? "Analysing..."
            : "Load Demo CSV"}
        </button>

      </div>

    </section>
  );
}


export default UploadPanel;