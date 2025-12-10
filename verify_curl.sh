#!/bin/bash
BASE_DIR="/Users/vc/Library/CloudStorage/OneDrive-BIRLAINSTITUTEOFTECHNOLOGYandSCIENCE/Documents/coding/AI_exam_corrector/comprehensive_test_data"
SOLUTION="$BASE_DIR/solution_key.txt"

echo "Solution Key: $SOLUTION"

# Construct curl command
CMD="curl -v -X POST http://127.0.0.1:8000/api/grade/ \
  -F \"solutionKey=@$SOLUTION\""

# Add student files
for file in "$BASE_DIR"/student_*.txt; do
    echo "Adding student file: $file"
    CMD="$CMD -F \"studentSheet=@$file\""
done

echo "Executing command..."
eval $CMD
