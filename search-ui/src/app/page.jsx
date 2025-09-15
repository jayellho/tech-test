"use client";

import React from "react";
import { SearchProvider } from "@elastic/react-search-ui";
import ElasticsearchAPIConnector from "@elastic/search-ui-elasticsearch-connector";
import "@elastic/react-search-ui-views/lib/styles/styles.css";
import { CVSearchUI } from "./search/CVSearchUI";

const connector = new ElasticsearchAPIConnector({
  host: process.env.NEXT_PUBLIC_ES_HOST,
  index: process.env.NEXT_PUBLIC_ES_INDEX
});

const config = {
  alwaysSearchOnInitialLoad: true,
  apiConnector: connector,
  initialState: { resultsPerPage: 10 },
  searchQuery: {
    // search in the transcribed text
    search_fields: { generated_text: {} },

    // fields returned for results
    result_fields: {
      generated_text: { snippet: { size: 300, fallback: true } },
      duration: { raw: {} },
      age: { raw: {} },
      gender: { raw: {} },
      accent: { raw: {} },
      filename: { raw: {} },
      path: { raw: {} }, // filename is stored in this field
    },

    // facets/filters on keyword fields
    facets: {
      age: { type: "value", size: 50 },
      gender: { type: "value", size: 10 },
      accent: { type: "value", size: 100 },
      duration_bucket: { type: "value", size: 10 }
    }
  }
};

export default function Page() {
  return (
    <main className="p-6">
      <h1 className="text-2xl font-semibold mb-4">Common Voice Search</h1>
      <SearchProvider config={config}>
        <CVSearchUI />
      </SearchProvider>
    </main>
  );
}
