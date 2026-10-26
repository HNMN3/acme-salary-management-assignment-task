import { Badge, Container, Group, Title } from "@mantine/core";
import { useEffect, useState } from "react";

import { getHealth } from "./api/health";

type BackendState = "checking" | "online" | "offline";

const BADGE_COLOR: Record<BackendState, string> = {
  checking: "gray",
  online: "green",
  offline: "red",
};

export default function App() {
  const [backend, setBackend] = useState<BackendState>("checking");

  useEffect(() => {
    getHealth()
      .then(() => setBackend("online"))
      .catch(() => setBackend("offline"));
  }, []);

  return (
    <Container size="xl" py="md">
      <Group justify="space-between">
        <Title order={2}>ACME Salary Management</Title>
        <Badge color={BADGE_COLOR[backend]}>Backend {backend}</Badge>
      </Group>
    </Container>
  );
}
