# AI Router V5 Implementation

AI Router V5 receives a natural-language question and returns:

- Intent
- Business object
- Required agents
- Required data

The Flask workspace calls the shared FoxBrain V5 contract in `foxbrain_os.ai_os_v5` and stores route context in each AI run. The route context removes manual user configuration and preserves read-only Core linkage.

## Examples

- `南山店最近经营怎么样？` routes Store-focused questions to Store and Commerce/Customer context.
- `为什么利润下降？` routes to Finance Agent and Commerce Agent.
- `Osprey库存风险？` routes to Supply Agent and Core Inventory data.
