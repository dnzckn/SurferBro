#!/bin/bash
# SUPER quick 5-minute demo

echo "============================================================"
echo "🏄 SurferBro SUPER QUICK DEMO - 5 Minutes"
echo "============================================================"
echo ""
echo "Ultra-fast training just to see it work!"
echo "Timesteps: 25,000 (~5 minutes)"
echo ""
read -p "Press ENTER to start..."

surferbro-train \
  --ocean ocean_designs/ocean_design_20251026_150514.json \
  --timesteps 25000 \
  --n-envs 4 \
  --algorithm SAC \
  --save-freq 5000 \
  --eval-freq 5000

echo ""
echo "✅ Super quick demo done!"
echo ""

# Evaluate
LATEST_MODEL=$(ls -td trained_models/surferbro_*/best_model/best_model.zip 2>/dev/null | head -1)

if [ -n "$LATEST_MODEL" ]; then
    echo "Watching the agent surf..."
    surferbro-evaluate --model "$LATEST_MODEL" --render --episodes 2
fi
