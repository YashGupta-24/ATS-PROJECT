import React, { useState } from "react";
import { GlobalWorkerOptions } from "pdfjs-dist";
import * as pdfjsLib from "pdfjs-dist/legacy/build/pdf";
import workerUrl from "pdfjs-dist/build/pdf.worker?url";

pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl;

function Form() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [jd, setJD] = useState("");
  const [pdfText, setPdfText] = useState("");
  const [error, setError] = useState(null);
  const [matchScore, setMatchScore] = useState(null);
  const [buttonVisible, setButtonVisible] = useState(true); 

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    setError(null);
    setPdfText("");
    setSelectedFile(null);
    setMatchScore(null);
    setButtonVisible(true); 

    if (!file) return;

    if (file.type !== "application/pdf") {
      alert("Please select a PDF file only");
      e.target.value = null;
      return;
    }

    setSelectedFile(file);

    const reader = new FileReader();
    reader.onload = async (evt) => {
      try {
        const typedArray = new Uint8Array(evt.target.result);
        const pdf = await pdfjsLib.getDocument({ data: typedArray }).promise;

        let completeText = "";
        for (let i = 1; i <= pdf.numPages; i++) {
          const page = await pdf.getPage(i);
          const content = await page.getTextContent();
          const pageText = content.items.map((item) => item.str).join(" ");
          completeText += pageText + "\n\n";
        }
        setPdfText(completeText);
      } catch (err) {
        console.error(err);
        setError("Failed to extract PDF text");
      }
    };
    reader.readAsArrayBuffer(file);
  };

  const handleJdChange = (e) => {
    setJD(e.target.value);
    setMatchScore(null);
    setButtonVisible(true); 
  };

  const handleMatchScore = async () => {
    if (!pdfText || !jd) {
      alert("Please upload a resume and enter a job description.");
      return;
    }

    try {
      setButtonVisible(false); 

      const response = await fetch("http://localhost:8080/match", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          resume_text: pdfText,
          jd: jd,
        }),
      });

      const data = await response.json();
      setMatchScore(data.match_score);
    } catch (err) {
      console.error(err);
      setError("Failed to fetch match score.");
    }
  };

  return (
    <div className="h-screen w-screen flex flex-col justify-center items-center gap-2 p-4">
      <div className="w-full flex justify-center items-center">
        <div className="h-fit w-1/2 border-[1px] border-blue-700 rounded-3xl flex p-4 gap-4">
          <div className="w-1/2 h-full p-4 flex flex-col gap-4">
            <h1>Upload your resume</h1>
            <div className="flex items-center justify-center w-full">
              <label
                htmlFor="dropzone-file"
                className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50"
              >
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <p className="mb-2 text-sm text-gray-500">
                    <span className="font-semibold">Click to upload</span> or drag and drop
                  </p>
                  <p className="text-xs text-gray-500">PDF only (1 MB max)</p>
                </div>
                <input
                  id="dropzone-file"
                  type="file"
                  accept="application/pdf"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </label>
            </div>
            {selectedFile && (
              <div className="mt-2 text-sm text-gray-700">
                <strong>Selected:</strong> {selectedFile.name}
              </div>
            )}
            {error && <div className="mt-2 text-red-600">Error: {error}</div>}
          </div>

          <div className="w-1/2 h-full p-4 flex flex-col gap-4">
            <h1>Enter Job Description</h1>
            <textarea
              className="w-full h-64 border-2 border-gray-300 border-dashed rounded-lg p-2 resize-none"
              placeholder="Software Engineering Intern Position"
              value={jd}
              onChange={handleJdChange}
            ></textarea>
          </div>
        </div>
      </div>

      {buttonVisible && (
        <div
          onClick={handleMatchScore}
          className="h-fit w-1/2 border-[1px] border-blue-700 rounded-xl p-4 text-center cursor-pointer hover:bg-blue-700 hover:text-white"
          id="match_button"
        >
          Match Score
        </div>
      )}

      {matchScore !== null && (
        <div className="mt-4 w-1/2 p-4 border rounded bg-gray-100 text-center">
          <p><strong>Match Score:</strong> {matchScore}/100</p>
        </div>
      )}
    </div>
  );
}

export default Form;
