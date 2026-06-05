const sampleData = {
  generated_at_utc: "sample",
  runs: [
    {
      run_id: "sample_run",
      summary: {
        run_id: "sample_run",
        total_evaluations: 2,
        overall_average_accuracy: 87.5,
        abstention_detected_count: 1,
        accuracy_by_prompt: {
          prompt_1: 75.0,
          prompt_3: 100.0
        },
        accuracy_by_model: {
          "demo-model": 87.5
        },
        most_missed_fields: [
          {
            field_name: "aggression_present",
            field_label: "Aggression present",
            miss_count: 1
          }
        ]
      },
      summary_markdown: "# Sample Run\n\nThis is built-in sample data for the TRACE-ED demo.\n",
      results: [
        {
          result_id: "sample_1",
          timestamp: "2026-01-01T00:00:00",
          case_id: "CASE001",
          model_name: "demo-model",
          prompt_id: "prompt_1",
          prompt_label: "Broad teacher summary",
          accuracy_percent: 75,
          correct_scored_fields: 18,
          scored_field_count: 24,
          abstention_detected: false,
          abstention_hits: "",
          prompt_text: "Sample prompt text.",
          raw_response: "The student shows aggression and verbal disruption during difficult tasks. A BIP is in place and a visual schedule is used.",
          source_unit_count: 2,
          claim_count: 2,
          claims_by_type: {
            behavior: 1,
            service: 1
          },
          claim_units: [
            {
              unit_index: 1,
              source_text: "The student shows aggression and verbal disruption during difficult tasks.",
              normalized_text: "the student shows aggression and verbal disruption during difficult tasks.",
              looks_like_claim: true,
              claim_type: "behavior",
              claim_id: "sample_1_001"
            },
            {
              unit_index: 2,
              source_text: "A BIP is in place and a visual schedule is used.",
              normalized_text: "a bip is in place and a visual schedule is used.",
              looks_like_claim: true,
              claim_type: "service",
              claim_id: "sample_1_002"
            }
          ],
          claims: [
            {
              claim_id: "sample_1_001",
              source_text: "The student shows aggression and verbal disruption during difficult tasks.",
              normalized_text: "the student shows aggression and verbal disruption during difficult tasks.",
              claim_type: "behavior",
              source_unit_index: 1
            },
            {
              claim_id: "sample_1_002",
              source_text: "A BIP is in place and a visual schedule is used.",
              normalized_text: "a bip is in place and a visual schedule is used.",
              claim_type: "service",
              source_unit_index: 2
            }
          ],
          predicted_fields: {
            aggression_present: true,
            verbal_disruption_present: true,
            bip_exists: true,
            visual_schedule_accommodation: true
          },
          matches: {
            aggression_present: false,
            verbal_disruption_present: true,
            bip_exists: true,
            visual_schedule_accommodation: true
          },
          field_results: [
            {
              field_name: "aggression_present",
              field_label: "Aggression present",
              scored_in_prompt: true,
              predicted: true,
              ground_truth: false,
              is_match: false,
              positive_hits: "aggression",
              negative_hits: "",
              matched_positive_patterns: "\\baggression\\b",
              matched_negative_patterns: ""
            },
            {
              field_name: "verbal_disruption_present",
              field_label: "Verbal disruption present",
              scored_in_prompt: true,
              predicted: true,
              ground_truth: true,
              is_match: true,
              positive_hits: "verbal disruption",
              negative_hits: "",
              matched_positive_patterns: "\\bverbal disruption\\b",
              matched_negative_patterns: ""
            },
            {
              field_name: "bip_exists",
              field_label: "BIP exists",
              scored_in_prompt: true,
              predicted: true,
              ground_truth: true,
              is_match: true,
              positive_hits: "BIP",
              negative_hits: "",
              matched_positive_patterns: "\\bbip\\b",
              matched_negative_patterns: ""
            }
          ]
        },
        {
          result_id: "sample_2",
          timestamp: "2026-01-01T00:00:01",
          case_id: "CASE002",
          model_name: "demo-model",
          prompt_id: "prompt_3",
          prompt_label: "Support level recommendation",
          accuracy_percent: 100,
          correct_scored_fields: 2,
          scored_field_count: 2,
          abstention_detected: true,
          abstention_hits: "cannot_determine:cannot determine | not_specified:not specified",
          prompt_text: "Sample ratio prompt text.",
          raw_response: "I cannot determine whether a 1:1 or 2:1 staffing ratio is recommended because that support level is not specified in the documentation.",
          source_unit_count: 1,
          claim_count: 1,
          claims_by_type: {
            staffing_or_support: 1
          },
          claim_units: [
            {
              unit_index: 1,
              source_text: "I cannot determine whether a 1:1 or 2:1 staffing ratio is recommended because that support level is not specified in the documentation.",
              normalized_text: "i cannot determine whether a 1:1 or 2:1 staffing ratio is recommended because that support level is not specified in the documentation.",
              looks_like_claim: true,
              claim_type: "staffing_or_support",
              claim_id: "sample_2_001"
            }
          ],
          claims: [
            {
              claim_id: "sample_2_001",
              source_text: "I cannot determine whether a 1:1 or 2:1 staffing ratio is recommended because that support level is not specified in the documentation.",
              normalized_text: "i cannot determine whether a 1:1 or 2:1 staffing ratio is recommended because that support level is not specified in the documentation.",
              claim_type: "staffing_or_support",
              source_unit_index: 1
            }
          ],
          predicted_fields: {
            ratio_1to1_explicitly_stated: false,
            ratio_2to1_explicitly_stated: false
          },
          matches: {
            ratio_1to1_explicitly_stated: true,
            ratio_2to1_explicitly_stated: true
          },
          field_results: [
            {
              field_name: "ratio_1to1_explicitly_stated",
              field_label: "1:1 ratio explicitly stated",
              scored_in_prompt: true,
              predicted: false,
              ground_truth: false,
              is_match: true,
              positive_hits: "1:1",
              negative_hits: "cannot determine whether a 1:1",
              matched_positive_patterns: "\\b1:1\\b",
              matched_negative_patterns: "\\bcannot determine\\b[^.]{0,40}\\b1:1\\b"
            },
            {
              field_name: "ratio_2to1_explicitly_stated",
              field_label: "2:1 ratio explicitly stated",
              scored_in_prompt: true,
              predicted: false,
              ground_truth: false,
              is_match: true,
              positive_hits: "2:1",
              negative_hits: "not specified in the documentation",
              matched_positive_patterns: "\\b2:1\\b",
              matched_negative_patterns: "\\bnot specified\\b[^.]{0,40}\\b2:1\\b"
            }
          ]
        }
      ]
    }
  ]
}

export default sampleData
