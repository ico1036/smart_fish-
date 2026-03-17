# NOTICE

## Original Work

SmartFish is based on [MiroFish](https://github.com/666ghj/MiroFish), originally created by [@666ghj](https://github.com/666ghj) and contributors, licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](https://www.gnu.org/licenses/agpl-3.0.html).

## Modifications (March 2026)

SmartFish is a derivative work with the following changes from the original MiroFish:

### Backend (completely rewritten)
- **Web framework**: Flask → FastAPI (async)
- **LLM provider**: OpenAI SDK → Anthropic Claude SDK
- **Knowledge graph**: Zep Cloud → NetworkX (in-memory)
- **Simulation engine**: OASIS/CAMEL-AI → Custom simulation engine
- **All backend Python code** was written from scratch, not copied from MiroFish

### Frontend (ported and adapted)
The following Vue.js components were ported from MiroFish's frontend with adaptations for SmartFish's API:

- `frontend/src/components/GraphPanel.vue` — D3.js graph visualization (copied, API endpoints adapted)
- `frontend/src/views/HomeView.vue` — Landing page (copied, branding changed to SmartFish)
- `frontend/src/views/MainView.vue` — Dual-panel workflow view (copied, API imports adapted)
- `frontend/src/views/SimulationRunView.vue` — Simulation monitoring (copied, API adapted)
- `frontend/src/views/ReportView.vue` — Report display (copied, API adapted)
- `frontend/src/views/InteractionView.vue` — Agent interaction/interview (copied, API adapted)
- `frontend/src/components/Step1GraphBuild.vue` — Ontology/graph build workflow (copied, API adapted)
- `frontend/src/components/Step2EnvSetup.vue` — Environment setup workflow (copied, API adapted)
- `frontend/src/components/Step3Simulation.vue` — Simulation timeline (copied, API adapted)
- `frontend/src/components/Step4Report.vue` — Report generation workflow (copied, API adapted)
- `frontend/src/components/Step5Interaction.vue` — Deep interaction chat (copied, API adapted)

All adaptations include:
- API endpoint URLs changed to match FastAPI routes
- Import paths updated for SmartFish's module structure
- Branding references changed from "MiroFish" to "SmartFish"

## License

This derivative work is distributed under the same [AGPL-3.0 License](LICENSE) as the original.

Copyright (c) 2025 MiroFish Contributors (original work)
Copyright (c) 2026 SmartFish Contributors (modifications)
