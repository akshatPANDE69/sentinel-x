use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub enum SessionState {
    STOPPED,
    STARTED,
    DISCOVERING,
    GAME_FOUND,
    SESSION_NEGOTIATING,
    ATTESTING,
    PROTECTED,
    DEGRADED,
    QUARANTINED,
    RECOVERING,
    RESTORED,
    ERROR,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionStateMachine {
    pub session_id: Option<String>,
    pub game_id: Option<String>,
    pub process_id: Option<u32>,
    pub state: SessionState,
}

impl SessionStateMachine {
    pub fn new() -> Self {
        Self {
            session_id: None,
            game_id: None,
            process_id: None,
            state: SessionState::STARTED,
        }
    }

    pub fn discover_game(&mut self, game_id: &str, pid: u32) {
        self.game_id = Some(game_id.to_string());
        self.process_id = Some(pid);
        self.state = SessionState::GAME_FOUND;
    }

    pub fn bind_session(&mut self, session_id: &str) {
        self.session_id = Some(session_id.to_string());
        self.state = SessionState::ATTESTING;
    }

    pub fn attest_verified(&mut self) {
        self.state = SessionState::PROTECTED;
    }

    pub fn quarantine(&mut self) {
        self.state = SessionState::QUARANTINED;
    }

    pub fn recover_restored(&mut self) {
        self.state = SessionState::RESTORED;
    }

    pub fn terminate(&mut self) {
        self.state = SessionState::STOPPED;
        self.session_id = None;
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_state_transitions() {
        let mut sm = SessionStateMachine::new();
        assert_eq!(sm.state, SessionState::STARTED);

        sm.discover_game("sx-arena", 4420);
        assert_eq!(sm.state, SessionState::GAME_FOUND);

        sm.bind_session("SX-1234");
        assert_eq!(sm.state, SessionState::ATTESTING);

        sm.attest_verified();
        assert_eq!(sm.state, SessionState::PROTECTED);
    }
}
