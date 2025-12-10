#!/bin/bash
BASE_DIR="/Users/vc/Library/CloudStorage/OneDrive-BIRLAINSTITUTEOFTECHNOLOGYandSCIENCE/Documents/coding/AI_exam_corrector/comprehensive_test_data"
SOLUTION="$BASE_DIR/solution_key.txt"
STUDENT="$BASE_DIR/student_mixed.txt"

echo "Testing single file: $STUDENT"

curl -v -X POST http://127.0.0.1:8000/api/grade/ \
  -F "solutionKey=@$SOLUTION" \
  -F "studentSheet=@$STUDENT"
