#!/bin/bash
# Train with the PROPER ocean design

echo "============================================================"
echo "🏄 Training SurferBro with PROPER Ocean"
echo "============================================================"
echo ""
echo "This ocean has:"
echo "  ✓ Beach (sand) for starting"
echo "  ✓ Depth gradient (shallow → deep)"
echo "  ✓ Proper wave zone"
echo ""
echo "Training configuration:"
echo "  Ocean: ocean_designs/proper_beach_ocean.json"
echo "  Algorithm: SAC (fast learning)"
echo "  Timesteps: 100,000"
echo "  Parallel Envs: 4"
echo "  Time: ~15-20 minutes"
echo ""
read -p "Press ENTER to start training..."

surferbro-train \
  --ocean ocean_designs/proper_beach_ocean.json \
  --timesteps 100000 \
  --n-envs 4 \
  --algorithm SAC \
  --eval-freq 100000

echo ""
echo "✅ Training complete!"
echo ""
echo "Watch your agent:"
echo "  surferbro-evaluate --model trained_models/surferbro_SAC_*/best_model/best_model.zip --render"
