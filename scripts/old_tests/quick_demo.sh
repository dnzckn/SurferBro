#!/bin/bash
# Quick 10-minute demo training

echo "============================================================"
echo "🏄 SurferBro QUICK DEMO - 10 Minute Training"
echo "============================================================"
echo ""
echo "This will train for just 50,000 steps (~10 minutes)"
echo "Good enough to see if the agent is learning!"
echo ""
echo "Ocean: Your custom design"
echo "Algorithm: PPO (PyTorch)"
echo "Timesteps: 50,000"
echo "Parallel Envs: 4"
echo ""
echo "Press Ctrl+C to stop your current training first, then run this."
echo ""
read -p "Press ENTER to start quick demo training..."

surferbro-train \
  --ocean ocean_designs/ocean_design_20251026_150514.json \
  --timesteps 50000 \
  --n-envs 4 \
  --algorithm PPO \
  --save-freq 10000 \
  --eval-freq 5000

echo ""
echo "✅ Quick demo complete!"
echo ""
echo "The agent has had basic training. Let's watch it!"
echo ""
echo "Running evaluation..."
echo ""

# Find the most recent model
LATEST_MODEL=$(ls -td trained_models/surferbro_PPO_*/best_model/best_model.zip 2>/dev/null | head -1)

if [ -n "$LATEST_MODEL" ]; then
    echo "Found model: $LATEST_MODEL"
    echo ""
    surferbro-evaluate --model "$LATEST_MODEL" --render --episodes 3
else
    echo "No model found. Check trained_models/ directory."
fi

echo ""
echo "Demo complete! 🏄‍♂️"
