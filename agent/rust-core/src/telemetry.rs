use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::VecDeque;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EngineOperation {
    pub operation: String,
    pub component: String,
    pub state: String, // "START" | "END"
    pub duration_ms: Option<f64>,
    pub result: Option<String>,
    pub timestamp: DateTime<Utc>,
}

pub struct TelemetryQueue<T> {
    buffer: VecDeque<T>,
    capacity: usize,
}

impl<T> TelemetryQueue<T> {
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: VecDeque::with_capacity(capacity),
            capacity,
        }
    }

    pub fn push(&mut self, item: T) {
        if self.buffer.len() >= self.capacity {
            self.buffer.pop_front();
        }
        self.buffer.push_back(item);
    }

    pub fn len(&self) -> usize {
        self.buffer.len()
    }

    pub fn is_empty(&self) -> bool {
        self.buffer.is_empty()
    }

    pub fn iter(&self) -> impl Iterator<Item = &T> {
        self.buffer.iter()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_bounded_queue() {
        let mut q = TelemetryQueue::<i32>::new(3);
        q.push(1);
        q.push(2);
        q.push(3);
        q.push(4);
        assert_eq!(q.len(), 3);
        let items: Vec<i32> = q.iter().copied().collect();
        assert_eq!(items, vec![2, 3, 4]);
    }
}
