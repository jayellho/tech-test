"use client";

import React from "react";
import {
  ErrorBoundary,
  Facet,
  SearchBox,
  Results,
  PagingInfo,
  ResultsPerPage,
  Paging,
  useSearch
} from "@elastic/react-search-ui";
import { Layout } from "@elastic/react-search-ui-views";
import "@elastic/react-search-ui-views/lib/styles/styles.css";

export function CVSearchUI() {
  const { wasSearched } = useSearch();

  return (
    <ErrorBoundary>
      <Layout
        header={
          <SearchBox
            searchAsYouType={true}
            debounceLength={200}
            inputProps={{ placeholder: "Search transcriptions (generated_text)..." }}
          />
        }
        sideContent={
          <div className="space-y-4">
            <Facet field="age" label="Age" />
            <Facet field="gender" label="Gender" />
            <Facet field="accent" label="Accent" />
            <Facet 
              field="duration_bucket" 
              label="Duration"
            />
          </div>
        }
        bodyHeader={
          <>
            {wasSearched && <PagingInfo />}
            {wasSearched && <ResultsPerPage options={[10, 20, 50]} />}
          </>
        }
        bodyContent={
          <Results
            resultView={({ result }) => {
              const text =
                result.generated_text?.snippet ||
                result.generated_text?.raw ||
                "";
              
              return (
                <div className="sui-result p-4 rounded-lg border mb-3">
                  <div 
                    className="sui-result__title text-lg font-medium"
                    dangerouslySetInnerHTML={{ __html: text.toString() }}
                  />
                  <div className="sui-result__details text-sm text-gray-700">
                    {result.duration?.raw && (
                      <>Duration: {result.duration.raw}s{" | "}</>
                    )}
                    {result.age?.raw && (
                      <>Age: {result.age.raw}{" | "}</>
                    )}
                    {result.gender?.raw && (
                      <>Gender: {result.gender.raw}{" | "}</>
                    )}
                    {result.accent?.raw && (
                      <>Accent: {result.accent.raw}{" | "}</>
                    )}
                    File: {result.filename?.raw ?? result.path?.raw ?? "Unknown"}
                  </div>
                </div>
              );
            }}
          />
        }
        bodyFooter={<Paging />}
      />
    </ErrorBoundary>
  );
}
