import { Center, Loader } from "@mantine/core";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <Center py="xl" role="status" aria-label={label}>
      <Loader />
    </Center>
  );
}
