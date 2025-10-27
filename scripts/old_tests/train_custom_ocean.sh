#!/bin/bash
# Quick training script for your custom ocean

echo "============================================================"
echo "🏄 SurferBro Training - Custom Ocean"
echo "============================================================"
echo ""
echo "Ocean: ocean_designs/ocean_design_20251026_150514.json"
echo "Algorithm: PPO (PyTorch)"
echo "Timesteps: 1,000,000"
echo "Parallel Envs: 4"
echo ""
echo "Expected time: ~15-20 minutes"
echo "Monitor with TensorBoard: tensorboard --logdir=logs/"
echo ""
echo "Starting training..."
echo ""

surferbro-train \
  --ocean ocean_designs/ocean_design_20251026_150514.json \
  --timesteps 1000000 \
  --n-envs 4 \
  --algorithm PPO \
  --save-freq 10000 \
  --eval-freq 5000

echo ""
echo "✅ Training complete!"
echo "Model saved in: trained_models/"
echo ""
echo "To watch your agent surf:"
echo "surferbro-evaluate --model trained_models/surferbro_PPO_*/best_model/best_model.zip --render"
