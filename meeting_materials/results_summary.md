# TRACE-ED Results Summary

These are the clean AWS Bedrock runs I have ready to discuss. Each run uses the same 10 synthetic TRACE-ED cases and the same 3 prompts, so each model has 30 evaluations total.

The demo export is currently set to show Bedrock runs only and to require at least 30 evaluations. That keeps the smoke test and the incomplete Claude run out of the demo view.

## Current Results

| Model | Run ID | Evaluations | Overall accuracy | Abstentions |
| --- | --- | ---: | ---: | ---: |
| Amazon Nova Micro | `aws_nova_micro_full10_pilot_01` | 30 | 80.78% | 0 |
| Amazon Nova Lite | `aws_nova_lite_full10_pilot_01` | 30 | 79.18% | 0 |
| Amazon Nova Pro | `aws_nova_pro_full10_pilot_01` | 30 | 80.60% | 0 |
| Meta Llama 3.3 70B | `aws_llama33_70b_full10_v1` | 30 | 79.59% | 0 |
| Mistral Large 3 | `aws_mistral_large3_full10_v1` | 30 | 81.13% | 1 |
| GPT OSS 20B | `aws_gpt_oss_20b_full10_v1` | 30 | 73.38% | 0 |

## Prompt Pattern

Prompt 3 is much easier than the other two prompts because it only asks for a support-level recommendation. Most models hit 100% on that prompt. Prompt 1 and Prompt 2 are more useful for seeing where the models struggle because they ask for broader details from the IEP/BIP text.

| Model | Prompt 1 | Prompt 2 | Prompt 3 |
| --- | ---: | ---: | ---: |
| Nova Micro | 67.08% | 75.26% | 100.00% |
| Nova Lite | 63.33% | 74.21% | 100.00% |
| Nova Pro | 69.17% | 72.63% | 100.00% |
| Llama 3.3 70B | 66.67% | 72.11% | 100.00% |
| Mistral Large 3 | 67.09% | 76.31% | 100.00% |
| GPT OSS 20B | 62.50% | 72.63% | 85.00% |

## What I Think This Shows

The first thing I notice is that the models are not wildly far apart on the full-run average. Mistral Large 3 is highest in this first group, but the Nova models and Llama are close enough that I would not overclaim anything yet.

The second thing is that the prompt matters. The broad teacher summary prompt is harder because it asks for more fields and gives the model more chances to miss something or add something unsupported. The behavior/supports prompt is a little more focused, so the scores are generally higher.

The third thing is that abstentions need to be tracked instead of treated as noise. Mistral had one abstention. That is not automatically bad. In this project, refusing to guess can sometimes be safer than inventing a detail that is not in the documents.

## Important Caveats

These are pilot/full-run results from the current prototype, not final scientific claims. The pipeline is now much better at saving audit files, separating error types, and showing claim support, but the scoring still needs spot-checking before I call these final results.

The scores are useful for comparing model behavior under the same setup. They are not proof that one model is safe for real special education use. The project is still about evaluation and traceability first.

## Runs Not Shown In The Demo

`aws_nova_micro_smoke_01` was a small AWS smoke test with only one case. It proved that Bedrock worked, but it should not be mixed into the full result table.

`aws_claude_haiku45_full10_v1` started but stopped because the Anthropic use-case form was not approved for the account. It should not be treated as a model result.
